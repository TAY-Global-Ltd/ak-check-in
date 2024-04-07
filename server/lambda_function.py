import json
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
    AK_CLASS_TIMETABLE_LAMBDA_MAP
)
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from typing import Optional
import boto3

TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)

logger = getLogger(__name__)

TEAMUP_API_KEY = get_secret("TEAMUP_API_KEY")

pnconfig = PNConfiguration()

pnconfig.subscribe_key = get_secret("PUB_NUB_SUBSCRIBE_KEY")
pnconfig.publish_key = get_secret("PUB_NUB_PUBLISH_KEY")
pnconfig.user_id = PUB_NUB_USER_ID
pubnub = PubNub(pnconfig)

AUTHORIZATION_TOKEN = get_secret("AUTHORIZATION_TOKEN")


class AuthorizationError(Exception):
    pass


def expose(f):
    f._IS_EXPOSED = True
    return f


def is_exposed(f):
    return getattr(f, "_IS_EXPOSED", False)


class Handler:
    def __init__(self, db, stage):
        self.api_key = TEAMUP_API_KEY
        self.db = db
        self.stage = stage
        self.check_in_minutes_before = 15

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
        return CAL_EVENT_ICON_BASE_FOLDER + CAL_EVENT_ICON_MAP[sub_calendar_id]

    @classmethod
    def _format_cal_event(cls, event: dict) -> dict:
        start_dt = datetime.fromisoformat(event["start_dt"])
        end_dt = datetime.fromisoformat(event["end_dt"])
        sub_cal = event["subcalendar_id"]

        return {
            "id": event["id"],
            "title": CAL_EVENT_TITLE[sub_cal],
            "description": event["title"],
            "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"),
            "icon": cls._get_icon(sub_cal),
            "icon_type": "url",
        }

    @expose
    def current_event(self, now: Optional[datetime] = None) -> dict:
        if now is None:
            now = datetime.now(TIME_ZONE)
        today = now.date()
        for event in self._get_events(today, today + timedelta(days=2)):
            end_dt = parser.parse(event["end_dt"])
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
        today = now.date()
        found_current = False
        for event in self._get_events(today, today + timedelta(days=2)):
            end_dt = parser.parse(event["end_dt"])
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
                "subscribe_key": pnconfig.subscribe_key,
                "user_id": PUB_NUB_USER_ID,
                "channel": PUB_NUB_CHANNEL_MAP[self.stage],
            },
            "attendees": attendees,
        }

    def _get_stars(self):
        return self.db["/rewards/stars"]

    def _process_action(self, event_id, u, stars, status, participant_id):
        participants = u.additional_participants()
        if participant_id >= 0 and participant_id < len(participants):
            participant = participants[participant_id]
            user_id = f"{u.email()}!{participant_id}"
            name = participant['alias']
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
        url = f"{CAL_BASE_URL}/events?startDate={start_dt}&endDate={end_dt}"
        res = requests.get(url, headers={"Teamup-Token": self.api_key})
        return res.json()["events"]

    def _get_participants(self, start_dt: date, end_dt: date):
        events = self._get_events(start_dt, end_dt)
        stars = self._get_stars()

        for event in events:
            users = {}
            event_id = event["id"]
            signups = self._signed_ups(event_id)

            for su in signups:
                u = self.db["/users/" + su['email']]
                pid = su['participant_id']
                users[f"{u.email()}!{pid}"] = (u, pid, "signedup")

            dt = parser.parse(event["start_dt"]).date()
            folder = self._checkin_folder(event_id, dt)

            for user_id in self.db.ls(folder):
                key = user_id
                if "!" in user_id:
                    user_id, pid = user_id.split("!")
                    pid = int(pid)
                else:
                    pid = -1

                u = self.db["/users/" + user_id]
                users[key] = (u, pid, "checkedin")

            return [
                self._process_action(event_id, u, stars, s, pid)
                for u, pid, s in users.values()
            ]

        raise KeyError(f"Cannot find any events between {start_dt} and {end_dt}")

    def _checkin_folder(self, evt_id, dt: date):
        return f"/checkins/{dt}/{evt_id}/"

    def _find_check_in_windows(self):
        dt = datetime.now(TIME_ZONE).today()
        for evt in self._get_events(dt, dt):
            start_dt, end_dt = [parser.parse(evt[x]) for x in ("start_dt", "end_dt")]
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
        url = f"{CAL_BASE_URL}/events/{event_id}"

        res = requests.get(url, headers={"Teamup-Token": self.api_key})
        return res.json()["event"]

    @expose
    def user_action(self, event_id, status, user_id, participant_id: int = -1):
        u = self.db["/users/" + user_id]
        stars = self._get_stars()

        message = self._process_action(event_id, u, stars, status, participant_id)
        print(f"Sending message: {message}")

        pubnub.publish().channel(PUB_NUB_CHANNEL_MAP[self.stage]).message(
            message
        ).sync()

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
        if method not in {"user_action"}:
            raise ValueError("Method not allowed")

        params = get_params(event, "kwargs")

    db = kydb.connect(f"dynamodb://" + TABLE_MAP[stage])
    db._cache = {}
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
