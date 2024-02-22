import json
from kms_utils import get_secret
import kydb
from logging import getLogger
from datetime import date, timedelta, datetime
import requests
from dateutil import parser
import pytz
from settings import (
    CAL_BASE_URL,
    CAL_EVENT_ICON_BASE_FOLDER,
    CAL_EVENT_ICON_MAP,
    TIME_ZONE_NAME,
    PUB_NUB_CHANNEL_MAP,
    PUB_NUB_USER_ID,
    TABLE_MAP
)

TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)

logger = getLogger(__name__)

TEAMUP_API_KEY = get_secret("TEAMUP_API_KEY")
PUB_NUB_PUBLISH_KEY = get_secret("PUB_NUB_PUBLISH_KEY"),


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
        folder = self._signup_folder(event_id)
        signups = (self.db[folder + "/" + x] for x in self.db.ls(folder))
        return [(x, x.user()) for x in signups]

    def _today(self):
        return datetime.now(TIME_ZONE).date()

    @staticmethod
    def _get_icon(sub_calendar_id):
        return CAL_EVENT_ICON_BASE_FOLDER + CAL_EVENT_ICON_MAP[sub_calendar_id]

    @classmethod
    def _format_cal_event(cls, event: dict) -> dict:
        start_dt = datetime.fromisoformat(event["start_dt"])
        end_dt = datetime.fromisoformat(event["end_dt"])

        return {
            "id": event["id"],
            "title": event["title"],
            "description": event["title"],
            "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"),
            "icon": cls._get_icon(event["subcalendar_id"]),
            "icon_type": "url",
        }

    @expose
    def current_event(self) -> dict:
        today = self._today()
        return self._format_cal_event(self._get_events(today, today)[0])

    @expose
    def next_event(self) -> dict:
        today = self._today()
        return self._format_cal_event(self._get_events(today, today)[1])

    @expose
    def initial_state(self):
        today = self._today()
        attendees = self._list(today, today)

        return {
            "subscription_info": {
                "subscribe_key": PUB_NUB_PUBLISH_KEY,
                "user_id": PUB_NUB_USER_ID,
                "channel": PUB_NUB_CHANNEL_MAP[self.stage],
            },
            "attendees": attendees,
        }

    def _get_stars(self):
        print('!' * 100)
        print(self.db)
        print('!' * 100)
        return self.db["/rewards/stars"]

    def _process_signup(self, event_id, s, u, stars):
        return {
            "event_id": event_id,
            "user-id": u.email(),
            "name": u.alias(),
            "icon": "person_check" if u.is_full_member() else "person_cancel",
            "icon_type": "material",
            "reward": "⭐" * stars.get(u.email(), 0),
            "status": "signedup",
        }

    def _get_events(self, start_dt: date, end_dt: date):
        url = f"{CAL_BASE_URL}/events?startDate={start_dt}&endDate={end_dt}"
        res = requests.get(url, headers={"Teamup-Token": self.api_key})
        return res.json()["events"]

    def _list(self, start_dt: date, end_dt: date):
        events = self._get_events(start_dt, end_dt)
        stars = self._get_stars()

        res = []

        for event in events:
            event_id = event["id"]
            signups = self._signed_ups(event_id)

            res += [self._process_signup(event_id, s, u, stars) for s, u in signups]

        return res

    def _signup_folder(self, event_id):
        return f"/signups/{event_id}"

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


def get_params(event, key):
    s = event.get(key)
    if s:
        if isinstance(s, str):
            return json.loads(s)

        return s

    return {}


def lambda_handler(event, context):
    print(event)

    if "requestContext" in event:
        stage = event["requestContext"]["stage"]
        if stage == 'test-invoke-stage':
            stage = 'uat'

        params = dict(
            **get_params(event, "queryStringParameters"), **get_params(event, "body")
        )

        path = event["path"].rsplit("/", 1)[1]
    else:
        stage = "prod"
        path = event.get("method", "send_class_confirmation")
        params = get_params(event, "kwargs")

    db = kydb.connect(f"dynamodb://" + TABLE_MAP[stage])
    db._cache = {}
    h = Handler(db, stage)

    f = getattr(h, path)
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
