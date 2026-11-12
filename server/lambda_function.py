import json
import settings
from lib.kms_utils import get_secret
import kydb
from logging import getLogger
from datetime import date, timedelta, datetime
import requests
from dateutil import parser
import pytz
from settings import (
    SETTINGS,
    CAL_BASE_URL,
    CAL_EVENT_ICON_BASE_FOLDER,
    CAL_EVENT_ICON_MAP,
    CAL_EVENT_TITLE,
    TIME_ZONE_NAME,
    PUB_NUB_CHANNEL_MAP,
    PUB_NUB_USER_ID,
    TABLE_MAP,
    AK_CLASS_TIMETABLE_LAMBDA_MAP,
)
try:
    from pubnub.pnconfiguration import PNConfiguration
    from pubnub.pubnub import PubNub
except ImportError:
    PNConfiguration = None
    PubNub = None
from typing import Optional
import boto3

TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)

# The gym a user_action is for selects its store, the same way ak-server's
# lib/gym_config.DB_SUFFIX does: each gym's users and stars live under the
# gym's prefix of the stage table (e.g. /diesel_gym/users/<id>). Keep the two
# in step; settings.GYM_DB_SUFFIX overrides it.
DEFAULT_GYM_ID = "diesel_ak"
GYM_DB_SUFFIX = getattr(
    settings,
    "GYM_DB_SUFFIX",
    {
        DEFAULT_GYM_ID: "",
        "diesel_gym": "/diesel_gym",
        "diesel_gym_tokyo": "/diesel_gym_tokyo",
        "diesel_gym_essex": "/diesel_gym_essex",
        "gracie_barra_chelmsford": "/gracie_barra_chelmsford",
        "gracie_barra_maldon": "/gracie_barra_maldon",
        "iga_academy": "/iga_academy",
        "igs_academy": "/igs_academy",
        # ak-server's smoke-test demo gym: its smoke users sign up and check
        # in too, so their notifications must not be skipped as unknown.
        "kakuto_demo": "/kakuto_demo",
    },
)

logger = getLogger(__name__)

try:
    TEAMUP_API_KEY = get_secret("TEAMUP_API_KEY")
except Exception as e:
    logger.warning("Could not load TEAMUP_API_KEY: %s", e)
    TEAMUP_API_KEY = None

if PNConfiguration:
    pnconfig = PNConfiguration()
    try:
        pnconfig.subscribe_key = get_secret("PUB_NUB_SUBSCRIBE_KEY")
        pnconfig.publish_key = get_secret("PUB_NUB_PUBLISH_KEY")
        pnconfig.user_id = PUB_NUB_USER_ID
        pubnub = PubNub(pnconfig)
    except Exception as e:
        logger.warning("Could not initialize PubNub: %s", e)
        pubnub = None
else:
    pnconfig = None
    pubnub = None

try:
    AUTHORIZATION_TOKEN = get_secret("AUTHORIZATION_TOKEN")
except Exception as e:
    logger.warning("Could not load AUTHORIZATION_TOKEN: %s", e)
    AUTHORIZATION_TOKEN = None


class AuthorizationError(Exception):
    pass


def expose(f):
    f._IS_EXPOSED = True
    return f


def is_exposed(f):
    return getattr(f, "_IS_EXPOSED", False)


class Handler:
    def __init__(self, db, stage, connect=None):
        self.api_key = TEAMUP_API_KEY
        self.db = db
        self.stage = stage
        self.check_in_minutes_before = 15
        # url -> kydb connection; the per-gym stores are opened on demand.
        self._connect = connect or _connect_db
        self._gym_dbs = {}

    def _gym_db(self, gym_id):
        """The store of ``gym_id`` (the default gym's is ``self.db``), or
        ``None`` if the gym is not configured."""
        if not gym_id or gym_id == DEFAULT_GYM_ID:
            return self.db
        suffix = GYM_DB_SUFFIX.get(gym_id)
        if suffix is None:
            return None
        if not suffix:
            return self.db
        if gym_id not in self._gym_dbs:
            self._gym_dbs[gym_id] = self._connect(
                "dynamodb://" + TABLE_MAP[self.stage] + suffix
            )
        return self._gym_dbs[gym_id]

    def _is_kakuto(self) -> bool:
        try:
            if hasattr(self.db, "exists"):
                if not self.db.exists("/configs/timetable"):
                    return False
            elif "/configs/timetable" not in self.db:
                return False
            cfg = self.db["/configs/timetable"]
            return isinstance(cfg, dict) and cfg.get("provider") == "kakuto"
        except Exception:
            return False

    def _signed_ups(self, event_id):
        client = boto3.client("lambda")
        payload = {
            "stage": self.stage,
            "method": "signups_for_event",
            "kwargs": {"event_id": event_id, "is_privilaged": True},
            "user_id": "demo-user@artillerykai.co.uk",
        }
        payload = json.dumps(payload).encode()

        res = client.invoke(
            FunctionName=AK_CLASS_TIMETABLE_LAMBDA_MAP[self.stage],
            InvocationType="RequestResponse",
            Payload=payload,
        )
        return json.loads(json.loads(res["Payload"].read())["body"])

    def _today(self):
        return datetime.now(TIME_ZONE).date()

    @staticmethod
    def _get_icon(sub_calendar_id):
        icon = CAL_EVENT_ICON_MAP.get(sub_calendar_id, "default.png")
        return CAL_EVENT_ICON_BASE_FOLDER + icon

    @classmethod
    def _format_cal_event(cls, event: dict) -> dict:
        start_dt = event["start_dt"]
        if isinstance(start_dt, str):
            start_dt = parser.parse(start_dt)
        end_dt = event["end_dt"]
        if isinstance(end_dt, str):
            end_dt = parser.parse(end_dt)
        sub_cal = event.get("subcalendar_id")

        return {
            "id": event["id"],
            "title": CAL_EVENT_TITLE.get(sub_cal, event.get("title", "Class")),
            "description": event.get("title", ""),
            "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"),
            "icon": cls._get_icon(sub_cal),
            "icon_type": "url",
        }

    @expose
    def current_event(self, now: Optional[datetime] = None) -> dict:
        if now is None:
            now = datetime.now(TIME_ZONE)
        else:
            if isinstance(now, str):
                now = parser.parse(now)
            if now.tzinfo is None:
                now = TIME_ZONE.localize(now)
        today = now.date()
        for event in self._get_events(today, today + timedelta(days=2)):
            end_dt = event["end_dt"]
            if isinstance(end_dt, str):
                end_dt = parser.parse(end_dt)
            if end_dt.tzinfo is None:
                end_dt = TIME_ZONE.localize(end_dt)
            if now <= end_dt:
                print(now, end_dt)
                return self._format_cal_event(event)

        raise ValueError("Cannot find any event ending after current time")

    @expose
    def next_event(self, now: Optional[datetime] = None) -> dict:
        # TODO: Little inefficient to do current_event and next_event
        # as separate queries. Let's put them together.
        # See: https://github.com/tayglobal/ak-check-in/issues/54
        if now is None:
            now = datetime.now(TIME_ZONE)
        else:
            if isinstance(now, str):
                now = parser.parse(now)
            if now.tzinfo is None:
                now = TIME_ZONE.localize(now)
        today = now.date()
        found_current = False
        for event in self._get_events(today, today + timedelta(days=2)):
            end_dt = event["end_dt"]
            if isinstance(end_dt, str):
                end_dt = parser.parse(end_dt)
            if end_dt.tzinfo is None:
                end_dt = TIME_ZONE.localize(end_dt)
            if now < end_dt:
                if found_current:
                    return self._format_cal_event(event)
                else:
                    found_current = True

        raise ValueError("Cannot find any event starting after current time")

    @expose
    def initial_state(self):
        today = self._today()
        attendees = self._get_participants(today, today + timedelta(days=1))

        return {
            "settings": SETTINGS,
            "subscription_info": {
                "subscribe_key": pnconfig.subscribe_key if pnconfig else "",
                "user_id": PUB_NUB_USER_ID,
                "channel": PUB_NUB_CHANNEL_MAP[self.stage],
            },
            "attendees": attendees,
        }

    def _get_stars(self, db=None):
        db = self.db if db is None else db
        try:
            return db["/rewards/stars"]
        except KeyError:
            return {}

    def _process_action(self, event_id, u, stars, status, participant_id):
        participants = u.additional_participants()
        if participant_id >= 0 and participant_id < len(participants):
            participant = participants[participant_id]
            user_id = f"{u.email()}!{participant_id}"
            name = participant["alias"]
            parent_name = u.alias()
            icon = "supervisor_account"
        else:
            user_id = u.email()
            name = u.alias()
            parent_name = None
            icon = "person_check"

        return {
            "event_id": event_id,
            "user-id": user_id,
            "name": name,
            "parent_name": parent_name,
            "icon": icon if u.is_full_member() else "person_cancel",
            "icon_type": "material",
            "reward": "⭐" * stars.get(u.email(), 0),
            "status": status,
        }

    def _get_events(self, start_dt: date, end_dt: date):
        if self._is_kakuto():
            # Try provider abstraction if available
            try:
                from calendar_provider import make_provider

                provider = make_provider(self.db, self.stage)
                return provider.get_events(start_dt, end_dt)
            except (ImportError, Exception) as e:
                logger.info(
                    "Provider abstraction not available (%s), using lambda invocation",
                    e,
                )

            client = boto3.client("lambda")
            payload = {
                "stage": self.stage,
                "method": "get_classes",
                "kwargs": {
                    "start_date": str(start_dt),
                    "end_date": str(end_dt),
                    "include_num_attendees": False,
                },
                "user_id": "demo-user@artillerykai.co.uk",
            }
            res = client.invoke(
                FunctionName=AK_CLASS_TIMETABLE_LAMBDA_MAP[self.stage],
                InvocationType="RequestResponse",
                Payload=json.dumps(payload).encode(),
            )
            raw_payload = res["Payload"].read()
            resp_body = json.loads(raw_payload)
            if isinstance(resp_body, dict) and "body" in resp_body:
                data = (
                    json.loads(resp_body["body"])
                    if isinstance(resp_body["body"], str)
                    else resp_body["body"]
                )
            else:
                data = resp_body
            if isinstance(data, dict) and "events" in data:
                return data["events"]
            return data

        url = f"{CAL_BASE_URL}/events?startDate={start_dt}&endDate={end_dt}"
        res = requests.get(url, headers={"Teamup-Token": self.api_key})
        return res.json()["events"]

    def _get_participants(self, start_dt: date, end_dt: date):
        events = self._get_events(start_dt, end_dt)
        stars = self._get_stars()

        res = []

        for event in events:
            users = {}
            event_id = event["id"]
            signups = self._signed_ups(event_id)

            for su in signups:
                u = self.db["/users/" + su["email"]]
                pid = su["participant_id"]
                key = f"{u.email()}!{pid}" if pid >= 0 else u.email()
                users[key] = (u, pid, "signedup")

            start_dt_val = event["start_dt"]
            dt = (
                parser.parse(start_dt_val).date()
                if isinstance(start_dt_val, str)
                else start_dt_val.date()
            )
            folder = self._checkin_folder(event_id, dt)

            for user_id in self.db.ls(folder):
                key = user_id
                if "!" in user_id:
                    user_id, pid = user_id.split("!")
                    pid = int(pid)
                    if pid < 0:
                        key = user_id
                else:
                    pid = -1

                u = self.db["/users/" + user_id]
                users[key] = (u, pid, "checkedin")
                if pid < 0 and f"{user_id}!-1" in users and key != f"{user_id}!-1":
                    del users[f"{user_id}!-1"]

            res += [
                self._process_action(event_id, u, stars, s, pid)
                for u, pid, s in users.values()
            ]

        return res

    def _checkin_folder(self, evt_id, dt: date):
        return f"/checkins/{dt}/{evt_id}/"

    def _find_check_in_windows(self):
        dt = self._today()
        for evt in self._get_events(dt, dt):
            start_dt = evt["start_dt"]
            if isinstance(start_dt, str):
                start_dt = parser.parse(start_dt)
            end_dt = evt["end_dt"]
            if isinstance(end_dt, str):
                end_dt = parser.parse(end_dt)
            evt["check_in_window"] = (
                start_dt - timedelta(minutes=self.check_in_minutes_before),
                end_dt,
            )
            yield evt

    def _find_checkins(self, dt: date):
        res = []
        folder = f"/checkins/{dt}/"
        for evt_id in self.db.ls(folder):
            res += list(self.db.ls(folder + evt_id))

        return res

    def _get_event(self, event_id):
        if self._is_kakuto():
            try:
                from calendar_provider import make_provider

                provider = make_provider(self.db, self.stage)
                return provider.get_event(event_id)
            except (ImportError, Exception) as e:
                logger.info(
                    "Provider abstraction not available (%s), using lambda invocation",
                    e,
                )

            client = boto3.client("lambda")
            payload = {
                "stage": self.stage,
                "method": "get_events",
                "kwargs": {"event_ids": [event_id]},
                "user_id": "demo-user@artillerykai.co.uk",
            }
            res = client.invoke(
                FunctionName=AK_CLASS_TIMETABLE_LAMBDA_MAP[self.stage],
                InvocationType="RequestResponse",
                Payload=json.dumps(payload).encode(),
            )
            raw_payload = res["Payload"].read()
            resp_body = json.loads(raw_payload)
            if isinstance(resp_body, dict) and "body" in resp_body:
                data = (
                    json.loads(resp_body["body"])
                    if isinstance(resp_body["body"], str)
                    else resp_body["body"]
                )
            else:
                data = resp_body
            if isinstance(data, list) and data:
                return data[0]
            raise ValueError(f"Event {event_id} not found")

        url = f"{CAL_BASE_URL}/events/{event_id}"
        res = requests.get(url, headers={"Teamup-Token": self.api_key})
        return res.json()["event"]

    @expose
    def user_action(
        self, event_id, status, user_id, participant_id: int = -1, gym_id=None
    ):
        """Publish a sign-up/check-in/cancel to the live feed.

        ``gym_id`` (sent by ak-class-timetable) selects the store the user and
        stars are read from; absent means the default gym. An unknown gym or a
        user missing from the store is logged at WARNING and skipped: this is
        invoked asynchronously, so raising only made Lambda retry it.
        """
        db = self._gym_db(gym_id)
        if db is None:
            logger.warning(
                "user_action: unknown gym_id %r for %s on %s; skipped",
                gym_id,
                user_id,
                event_id,
            )
            return None
        path = "/users/" + user_id
        try:
            u = db[path]
        except KeyError:
            logger.warning(
                "user_action: no user %s in gym %s; skipped %s on %s",
                path,
                gym_id or DEFAULT_GYM_ID,
                status,
                event_id,
            )
            return None
        stars = self._get_stars(db)

        message = self._process_action(event_id, u, stars, status, participant_id)
        print(f"Sending message: {message}")

        if pubnub is not None:
            try:
                envelope = (
                    pubnub.publish()
                    .channel(PUB_NUB_CHANNEL_MAP[self.stage])
                    .message(message)
                    .sync()
                )
                print("Publish time: %d" % envelope.result.timetoken)
            except Exception as e:
                print("Error: %s" % e)


def _connect_db(url):
    db = kydb.connect(url)
    db._cache = {}
    return db


def get_params(event, key):
    s = event.get(key)
    if s:
        if isinstance(s, str):
            return json.loads(s)

        return s

    return {}


def _check_authorization(event):
    _auth_type, token = event["headers"].get("Authorization").split(" ")
    if AUTHORIZATION_TOKEN != token:
        raise AuthorizationError("Unauthorized")


def lambda_handler(event, context):
    print(event)

    if "requestContext" in event:
        stage = event["requestContext"]["stage"]
        if stage == "test-invoke-stage":
            stage = "uat"

        _check_authorization(event)

        params = dict(
            **get_params(event, "queryStringParameters"), **get_params(event, "body")
        )

        method = event["path"].rsplit("/", 1)[1]
    else:
        # Internal only not exposed
        stage = event["stage"]
        method = event["method"]
        if method not in {"user_action", "current_event", "next_event", "initial_state"}:
            raise ValueError("Method not allowed")

        params = get_params(event, "kwargs")
        if event.get("gym_id") and "gym_id" not in params:
            params["gym_id"] = event["gym_id"]

    db = _connect_db(f"dynamodb://" + TABLE_MAP[stage])
    h = Handler(db, stage)

    f = getattr(h, method)
    if is_exposed(f):
        if not params:
            params = {}
        body = f(**params)
    else:
        raise ValueError("Path is not mapped")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
        "body": json.dumps(body),
    }
