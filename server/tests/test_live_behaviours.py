"""The behaviours that ran in prod from the 2026-10-10 deploy but were never
committed (ak-check-in live-only patch): optional PubNub/secrets, a single
guarded publish, kakuto-provider classes from ak-class-timetable, tolerant
event parsing, initial_state without PubNub, participant de-dup and the
internal method allow-list."""

import importlib.util
import json
import sys
import uuid
from datetime import date, datetime

import kydb
import pytest

import lambda_function
from lambda_function import Handler

from test_user_action import FakePubNub, FakeUser, published


@pytest.fixture
def pubnub(monkeypatch):
    fake = FakePubNub()
    monkeypatch.setattr(lambda_function, "pubnub", fake)
    return fake


@pytest.fixture
def db():
    return kydb.connect(f"memory://{uuid.uuid4()}")


@pytest.fixture
def connect(monkeypatch, db):
    """lambda_handler's root store is ``db``."""
    monkeypatch.setattr(lambda_function, "_connect_db", lambda url: db)
    return db


class FakeLambda:
    """boto3 lambda client: answers like ak-class-timetable (API-style body)."""

    def __init__(self, body):
        self.body = body
        self.calls = []

    def invoke(self, FunctionName, InvocationType, Payload):
        self.calls.append(
            {
                "function": FunctionName,
                "type": InvocationType,
                "payload": json.loads(Payload.decode()),
            }
        )
        raw = json.dumps({"statusCode": 200, "body": json.dumps(self.body)})

        class P:
            def read(self):
                return raw.encode()

        return {"Payload": P()}


def kakuto_db(db):
    db["/configs/timetable"] = {"provider": "kakuto", "kakuto": {"calendars": []}}
    return db


def stub_lambda(monkeypatch, body):
    fake = FakeLambda(body)
    monkeypatch.setattr(lambda_function.boto3, "client", lambda service: fake)
    # calendar_provider is not packaged; make sure the invoke path runs.
    monkeypatch.setitem(sys.modules, "calendar_provider", None)
    return fake


def no_teamup(monkeypatch):
    def fail(*a, **k):
        raise AssertionError("Teamup must not be called for a kakuto gym")

    monkeypatch.setattr(lambda_function.requests, "get", fail)


# 1. The module loads without PubNub or secrets.


def test_module_loads_without_pubnub_or_secrets(monkeypatch):
    kms = sys.modules["lib.kms_utils"]

    def no_secret(name):
        raise RuntimeError("no KMS")

    monkeypatch.setattr(kms, "get_secret", no_secret)
    monkeypatch.setitem(sys.modules, "pubnub", None)
    monkeypatch.setitem(sys.modules, "pubnub.pnconfiguration", None)
    monkeypatch.setitem(sys.modules, "pubnub.pubnub", None)
    spec = importlib.util.spec_from_file_location(
        "lambda_function_isolated", lambda_function.__file__
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.pubnub is None
    assert mod.pnconfig is None
    assert mod.TEAMUP_API_KEY is None
    assert mod.AUTHORIZATION_TOKEN is None


def test_module_loads_when_pubnub_secrets_fail(monkeypatch):
    kms = sys.modules["lib.kms_utils"]

    def secret(name):
        if name.startswith("PUB_NUB"):
            raise RuntimeError("no KMS")
        return "x"

    monkeypatch.setattr(kms, "get_secret", secret)
    spec = importlib.util.spec_from_file_location(
        "lambda_function_isolated2", lambda_function.__file__
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.pubnub is None
    assert mod.TEAMUP_API_KEY == "x"


# 2. user_action publishes once, and not at all without PubNub.


def test_user_action_publishes_exactly_once(db, pubnub):
    db["/users/a@x.com"] = FakeUser("a@x.com", "Alice")
    Handler(db, "prod").user_action("evt-1", "checkedin", "a@x.com")
    assert len(pubnub.messages) == 1
    [(channel, msg)] = published(pubnub)
    assert channel == "checkin-prod"
    assert msg["user-id"] == "a@x.com"


def test_user_action_without_pubnub_does_not_raise(db, monkeypatch):
    monkeypatch.setattr(lambda_function, "pubnub", None)
    db["/users/a@x.com"] = FakeUser("a@x.com", "Alice")
    assert Handler(db, "prod").user_action("evt-1", "checkedin", "a@x.com") is None


def test_user_action_publish_error_is_swallowed(db, monkeypatch):
    class Broken(FakePubNub):
        def sync(self):
            raise RuntimeError("pubnub down")

    broken = Broken()
    monkeypatch.setattr(lambda_function, "pubnub", broken)
    db["/users/a@x.com"] = FakeUser("a@x.com", "Alice")
    Handler(db, "prod").user_action("evt-1", "signedup", "a@x.com")
    assert len(broken.messages) == 1


# 3. A kakuto-provider gym takes its classes from ak-class-timetable.


KC_EVENT = {
    "id": "kc_evt_1",
    "title": "Wrestling",
    "subcalendar_id": 11273394,
    "start_dt": "2026-09-07T18:00:00+01:00",
    "end_dt": "2026-09-07T19:00:00+01:00",
}


@pytest.mark.parametrize("stage, fn", [("uat", "ak-class-timetable-uat"), ("prod", "ak-class-timetable")])
def test_kakuto_get_events_invokes_class_timetable(db, monkeypatch, stage, fn):
    no_teamup(monkeypatch)
    fake = stub_lambda(monkeypatch, {"events": [KC_EVENT]})
    h = Handler(kakuto_db(db), stage)
    events = h._get_events(date(2026, 9, 7), date(2026, 9, 9))
    assert events == [KC_EVENT]
    [call] = fake.calls
    assert call["function"] == fn
    assert call["type"] == "RequestResponse"
    assert call["payload"]["stage"] == stage
    assert call["payload"]["method"] == "get_classes"
    assert call["payload"]["kwargs"] == {
        "start_date": "2026-09-07",
        "end_date": "2026-09-09",
        "include_num_attendees": False,
    }


def test_kakuto_get_events_accepts_a_bare_list(db, monkeypatch):
    no_teamup(monkeypatch)
    stub_lambda(monkeypatch, [KC_EVENT])
    assert Handler(kakuto_db(db), "uat")._get_events(date(2026, 9, 7), date(2026, 9, 7)) == [KC_EVENT]


def test_kakuto_get_event_invokes_class_timetable(db, monkeypatch):
    no_teamup(monkeypatch)
    fake = stub_lambda(monkeypatch, [KC_EVENT])
    assert Handler(kakuto_db(db), "prod")._get_event("kc_evt_1") == KC_EVENT
    [call] = fake.calls
    assert call["payload"]["method"] == "get_events"
    assert call["payload"]["kwargs"] == {"event_ids": ["kc_evt_1"]}


def test_kakuto_get_event_missing_raises(db, monkeypatch):
    stub_lambda(monkeypatch, [])
    with pytest.raises(ValueError):
        Handler(kakuto_db(db), "prod")._get_event("nope")


def test_kakuto_current_event_end_to_end(db, monkeypatch):
    no_teamup(monkeypatch)
    stub_lambda(monkeypatch, {"events": [KC_EVENT]})
    now = lambda_function.TIME_ZONE.localize(datetime(2026, 9, 7, 18, 30))
    evt = Handler(kakuto_db(db), "uat").current_event(now)
    assert evt["id"] == "kc_evt_1"
    assert evt["start_time"] == "18:00"


def test_teamup_gym_still_uses_teamup(db, monkeypatch):
    calls = []

    class R:
        def json(self):
            return {"events": [KC_EVENT]}

    def get(url, headers):
        calls.append(url)
        return R()

    monkeypatch.setattr(lambda_function.requests, "get", get)
    monkeypatch.setattr(
        lambda_function.boto3, "client", lambda s: pytest.fail("no invoke for Teamup")
    )
    db["/configs/timetable"] = {"provider": "teamup"}
    Handler(db, "uat")._get_events(date(2026, 9, 7), date(2026, 9, 7))
    assert len(calls) == 1 and "startDate=2026-09-07" in calls[0]


# 4. Tolerant parsing: datetime or str times, str or naive `now`, unknown
#    subcalendars fall back.


def test_format_accepts_datetimes_and_unknown_subcalendar():
    tz = lambda_function.TIME_ZONE
    evt = {
        "id": "e",
        "title": "Capoeira",
        "subcalendar_id": 1,
        "start_dt": tz.localize(datetime(2026, 9, 7, 12)),
        "end_dt": tz.localize(datetime(2026, 9, 7, 13)),
    }
    out = Handler._format_cal_event(evt)
    assert out["title"] == "Capoeira"
    assert out["start_time"] == "12:00" and out["end_time"] == "13:00"
    assert out["icon"].endswith("default.png")


@pytest.mark.parametrize("now", ["2026-09-07T10:30:00", datetime(2026, 9, 7, 10, 30)])
def test_current_and_next_accept_str_or_naive_now(db, now):
    h = Handler(db, "uat")
    h._get_events = lambda s, e: [
        {"id": "a", "start_dt": "2026-09-07T10:00:00", "end_dt": "2026-09-07T11:00:00"},
        {"id": "b", "start_dt": "2026-09-07T11:00:00", "end_dt": "2026-09-07T12:00:00"},
    ]
    assert h.current_event(now)["id"] == "a"
    assert h.next_event(now)["id"] == "b"


def test_find_check_in_windows_uses_today(db):
    h = Handler(db, "uat")
    seen = []
    h._today = lambda: date(2026, 9, 7)

    def events(s, e):
        seen.append((s, e))
        return [{"id": "a", "start_dt": "2026-09-07T10:00:00+01:00", "end_dt": "2026-09-07T11:00:00+01:00"}]

    h._get_events = events
    [w] = list(h._find_check_in_windows())
    assert seen == [(date(2026, 9, 7), date(2026, 9, 7))]
    assert w["check_in_window"][0].strftime("%H:%M") == "09:45"


# 5. initial_state without PubNub.


def test_initial_state_without_pubnub(db, monkeypatch):
    monkeypatch.setattr(lambda_function, "pnconfig", None)
    h = Handler(db, "prod")
    h._get_participants = lambda s, e: []
    state = h.initial_state()
    assert state["subscription_info"]["subscribe_key"] == ""
    assert state["subscription_info"]["channel"] == "checkin-prod"
    assert state["attendees"] == []


# 6. Participant de-dup.


def participants_handler(db, signups, checkins):
    db["/users/a@x.com"] = FakeUser("a@x.com", "Alice", participants=[{"alias": "Kid"}])
    for c in checkins:
        db[f"/checkins/2026-09-07/evt-1/{c}"] = "checkedin"
    h = Handler(db, "uat")
    h._signed_ups = lambda event_id: signups
    h._get_events = lambda s, e: [
        {"id": "evt-1", "start_dt": "2026-09-07T10:00:00+01:00", "end_dt": "2026-09-07T11:00:00+01:00"}
    ]
    return h._get_participants(date(2026, 9, 7), date(2026, 9, 7))


@pytest.mark.parametrize("checkin_key", ["a@x.com", "a@x.com!-1"])
def test_signed_up_then_checked_in_member_appears_once(db, checkin_key):
    out = participants_handler(
        db, [{"email": "a@x.com", "participant_id": -1}], [checkin_key]
    )
    assert [(p["user-id"], p["status"]) for p in out] == [("a@x.com", "checkedin")]


def test_member_and_child_are_separate(db):
    out = participants_handler(
        db,
        [{"email": "a@x.com", "participant_id": -1}, {"email": "a@x.com", "participant_id": 0}],
        ["a@x.com!0"],
    )
    got = sorted((p["user-id"], p["status"]) for p in out)
    assert got == [("a@x.com", "signedup"), ("a@x.com!0", "checkedin")]


def test_signed_up_only(db):
    out = participants_handler(db, [{"email": "a@x.com", "participant_id": -1}], [])
    assert [(p["user-id"], p["status"]) for p in out] == [("a@x.com", "signedup")]


# 7. Internal (stage/method) allow-list.


@pytest.mark.parametrize("method", ["current_event", "next_event"])
def test_internal_event_methods_are_allowed(connect, monkeypatch, method):
    no_teamup(monkeypatch)
    stub_lambda(monkeypatch, {"events": [
        KC_EVENT,
        dict(KC_EVENT, id="kc_evt_2", start_dt="2026-09-07T19:00:00+01:00", end_dt="2026-09-07T20:00:00+01:00"),
    ]})
    kakuto_db(connect)
    res = lambda_function.lambda_handler(
        {"stage": "uat", "method": method, "kwargs": {"now": "2026-09-07T18:30:00+01:00"}},
        None,
    )
    assert res["statusCode"] == 200
    assert json.loads(res["body"])["id"] == ("kc_evt_1" if method == "current_event" else "kc_evt_2")


def test_internal_initial_state_is_allowed(connect, monkeypatch):
    monkeypatch.setattr(Handler, "_get_participants", lambda self, s, e: [])
    res = lambda_function.lambda_handler({"stage": "prod", "method": "initial_state"}, None)
    body = json.loads(res["body"])
    assert set(body) == {"settings", "subscription_info", "attendees"}


@pytest.mark.parametrize("method", ["_get_events", "_signed_ups", "lambda_handler", "nope"])
def test_internal_other_methods_are_refused(connect, method):
    with pytest.raises(ValueError, match="Method not allowed"):
        lambda_function.lambda_handler({"stage": "uat", "method": method}, None)
