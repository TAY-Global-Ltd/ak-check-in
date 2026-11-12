import lambda_function
import kydb
from pprint import pprint
from settings import TABLE_MAP
import requests
from datetime import datetime
import pytest
import json

stage = "uat"
event = {"requestContext": {"stage": stage}}

BASE_URL = "https://l6odffk4jd.execute-api.eu-west-2.amazonaws.com/uat/"
CURRENT_EVENT_URL = BASE_URL + "current_event"

try:
    db = kydb.connect("dynamodb://" + TABLE_MAP[stage])
    is_live_db = not isinstance(db, kydb.impl.memory.MemoryDB)
except Exception:
    db = kydb.connect("memory://test")
    is_live_db = False


@pytest.mark.skipif(not is_live_db, reason="Requires live DynamoDB connection")
def test_current_next_event():
    h = lambda_function.Handler(db, stage)
    now = datetime(2024, 2, 26, 8, 30, tzinfo=lambda_function.TIME_ZONE)
    events = h.current_event(now)
    print("-" * 80)
    print("[current_event]")
    pprint(events)

    print("-" * 80)
    print("[next_event]")
    events = h.next_event(now)
    pprint(events)


@pytest.mark.skipif(not is_live_db, reason="Requires live DynamoDB connection")
def test_initial_state():
    event = {
        "path": "/initial_state",
        "requestContext": {
            "stage": "uat",
        },
        "headers": {"Authorization": "Bearer MY_DUMMY_TOKEN"},
    }

    res = lambda_function.lambda_handler(event, None)
    body = json.loads(res["body"])
    pprint(body)
    expected = {"settings", "subscription_info", "attendees"}
    assert set(body.keys()) == expected

    event["headers"]["Authorization"] = "Bearer BAD_TOKEN"

    with pytest.raises(lambda_function.AuthorizationError):
        lambda_function.lambda_handler(event, None)


@pytest.mark.skipif(not is_live_db, reason="Requires live DynamoDB connection")
def test_checkin():
    event_id = _get_curr_event_id()
    # Checkin parent
    event = {
        "stage": "uat",
        "method": "user_action",
        "kwargs": {
            "event_id": event_id,
            "status": "checkedin",
            "user_id": "demo-user@artillerykai.co.uk",
        },
    }
    lambda_function.lambda_handler(event, None)

    # Checkin child
    event = {
        "stage": "uat",
        "method": "user_action",
        "kwargs": {
            "event_id": event_id,
            "status": "checkedin",
            "user_id": "demo-user@artillerykai.co.uk",
            "participant_id": 0,
        },
    }
    lambda_function.lambda_handler(event, None)


def _get_curr_event_id():
    h = lambda_function.Handler(db, stage)
    event = h.current_event()

    return event["id"]


def set_user(is_member=True):
    user = db["/users/demo-user@artillerykai.co.uk"]
    user.is_full_member.setvalue(is_member)
    user.additional_participants.setvalue(
        [
            {
                "name": "Baki Smith",
                "alias": "Baki-kun",
                "birthday": "2012-03-01",
                "gender": "male",
            },
            {
                "name": "Sakura Smith",
                "alias": "Sakura-chan",
                "birthday": "2015-02-05",
                "gender": "female",
            },
        ]
    )
    user.write()


@pytest.mark.skipif(not is_live_db, reason="Requires live DynamoDB connection")
def test_signup():
    set_user()
    event_id = _get_curr_event_id()
    event = {
        "stage": "uat",
        "method": "user_action",
        "kwargs": {
            "event_id": event_id,
            "status": "signedup",
            "user_id": "demo-user@artillerykai.co.uk",
            # Sign in the Second child
            "participant_id": 1,
        },
    }
    lambda_function.lambda_handler(event, None)


# ---------------------------------------------------------------------------
# Unit tests for Phase 3: Kakuto event IDs, subcalendars, and provider awareness
# ---------------------------------------------------------------------------


class MockUser:
    def __init__(
        self, email, alias="Demo User", is_full_member=True, participants=None
    ):
        self._email = email
        self._alias = alias
        self._is_full_member = is_full_member
        self._participants = participants or []

    def email(self):
        return self._email

    def alias(self):
        return self._alias

    def is_full_member(self):
        return self._is_full_member

    def additional_participants(self):
        return self._participants


def test_format_cal_event_with_teamup_and_kakuto_ids():
    """Verify _format_cal_event works with Teamup and synthetic kc_ event IDs,
    mapped disciplines (Wrestling, Judo, Running), and unknown subcalendars."""
    h = lambda_function.Handler(kydb.connect("memory://test_fmt"), "uat")

    # Teamup ID with Wrestling (11273394)
    teamup_event = {
        "id": "1616790286-rid-1713420000",
        "title": "Wrestling Fundamentals",
        "subcalendar_id": 11273394,
        "start_dt": "2026-09-07T18:00:00+01:00",
        "end_dt": "2026-09-07T19:00:00+01:00",
    }
    formatted = h._format_cal_event(teamup_event)
    assert formatted["id"] == "1616790286-rid-1713420000"
    assert formatted["title"] == "Wrestling"
    assert formatted["description"] == "Wrestling Fundamentals"
    assert formatted["start_time"] == "18:00"
    assert formatted["end_time"] == "19:00"
    assert formatted["icon"].endswith("wrestling.png")

    # Kakuto synthetic kc_ ID with Judo (10331322)
    kakuto_event = {
        "id": "kc_cal_judo_evt99_20260907T190000Z",
        "title": "Judo Open Mat",
        "subcalendar_id": 10331322,
        "start_dt": "2026-09-07T19:00:00+01:00",
        "end_dt": "2026-09-07T20:30:00+01:00",
    }
    formatted_kc = h._format_cal_event(kakuto_event)
    assert formatted_kc["id"] == "kc_cal_judo_evt99_20260907T190000Z"
    assert formatted_kc["title"] == "Judo"
    assert formatted_kc["description"] == "Judo Open Mat"
    assert formatted_kc["start_time"] == "19:00"
    assert formatted_kc["end_time"] == "20:30"
    assert formatted_kc["icon"].endswith("judo.png")

    # Running subcalendar (11086797)
    running_event = {
        "id": "kc_cal_run_evt1_20260907T070000Z",
        "title": "Morning Run",
        "subcalendar_id": 11086797,
        "start_dt": "2026-09-07T07:00:00+01:00",
        "end_dt": "2026-09-07T08:00:00+01:00",
    }
    formatted_run = h._format_cal_event(running_event)
    assert formatted_run["title"] == "Run Club"
    assert formatted_run["icon"].endswith("running.png")

    # Unmapped subcalendar should not crash with KeyError; fallbacks used
    unmapped_event = {
        "id": "kc_cal_unknown_evt1_20260907T120000Z",
        "title": "Capoeira Workshop",
        "subcalendar_id": 99999999,
        "start_dt": "2026-09-07T12:00:00+01:00",
        "end_dt": "2026-09-07T13:00:00+01:00",
    }
    formatted_unmapped = h._format_cal_event(unmapped_event)
    assert formatted_unmapped["title"] == "Capoeira Workshop"
    assert formatted_unmapped["icon"].endswith("default.png")


def test_current_and_next_event_resolution():
    """Verify current_event and next_event resolution with both Teamup and kc_ IDs."""
    mem_db = kydb.connect("memory://test_resolution")
    h = lambda_function.Handler(mem_db, "uat")

    mock_events = [
        {
            "id": "1616790286-rid-1713420000",
            "title": "Muay Thai All Levels",
            "subcalendar_id": 9946632,
            "start_dt": "2026-09-07T10:00:00+01:00",
            "end_dt": "2026-09-07T11:00:00+01:00",
        },
        {
            "id": "kc_cal_wrestling_master1_20260907T110000Z",
            "title": "Wrestling",
            "subcalendar_id": 11273394,
            "start_dt": "2026-09-07T11:00:00+01:00",
            "end_dt": "2026-09-07T12:00:00+01:00",
        },
        {
            "id": "kc_cal_bjj_master2_20260907T120000Z",
            "title": "BJJ Gi",
            "subcalendar_id": 9946633,
            "start_dt": "2026-09-07T12:00:00+01:00",
            "end_dt": "2026-09-07T13:00:00+01:00",
        },
    ]

    h._get_events = lambda start_dt, end_dt: mock_events

    # Current event during first class (10:30)
    now_1 = lambda_function.TIME_ZONE.localize(datetime(2026, 9, 7, 10, 30))
    curr_1 = h.current_event(now_1)
    assert curr_1["id"] == "1616790286-rid-1713420000"
    assert curr_1["title"] == "Muay Thai"

    next_1 = h.next_event(now_1)
    assert next_1["id"] == "kc_cal_wrestling_master1_20260907T110000Z"
    assert next_1["title"] == "Wrestling"

    # Current event during second class (11:15) with synthetic kc_ ID
    now_2 = lambda_function.TIME_ZONE.localize(datetime(2026, 9, 7, 11, 15))
    curr_2 = h.current_event(now_2)
    assert curr_2["id"] == "kc_cal_wrestling_master1_20260907T110000Z"
    assert curr_2["title"] == "Wrestling"

    next_2 = h.next_event(now_2)
    assert next_2["id"] == "kc_cal_bjj_master2_20260907T120000Z"
    assert next_2["title"] == "BJJ"


def test_find_check_in_windows():
    """Verify _find_check_in_windows computes window correctly for both ID schemes."""
    mem_db = kydb.connect("memory://test_windows")
    h = lambda_function.Handler(mem_db, "uat")

    mock_events = [
        {
            "id": "teamup_123",
            "title": "BJJ",
            "subcalendar_id": 9946633,
            "start_dt": "2026-09-07T10:00:00+01:00",
            "end_dt": "2026-09-07T11:00:00+01:00",
        },
        {
            "id": "kc_cal_wrestling_20260907T110000Z",
            "title": "Wrestling",
            "subcalendar_id": 11273394,
            "start_dt": "2026-09-07T11:00:00+01:00",
            "end_dt": "2026-09-07T12:00:00+01:00",
        },
    ]
    h._get_events = lambda start_dt, end_dt: mock_events

    windows = list(h._find_check_in_windows())
    assert len(windows) == 2
    win_start, win_end = windows[0]["check_in_window"]
    assert win_start.strftime("%H:%M") == "09:45"
    assert win_end.strftime("%H:%M") == "11:00"

    win_start_kc, win_end_kc = windows[1]["check_in_window"]
    assert win_start_kc.strftime("%H:%M") == "10:45"
    assert win_end_kc.strftime("%H:%M") == "12:00"


def test_get_participants_transparent_ids():
    """Verify _get_participants transparently handles Teamup IDs and kc_ IDs."""
    mem_db = kydb.connect("memory://test_participants")
    h = lambda_function.Handler(mem_db, "uat")

    mem_db["/rewards/stars"] = {"alice@test.com": 2, "bob@test.com": 1}
    mem_db["/users/alice@test.com"] = MockUser(
        "alice@test.com",
        alias="Alice",
        is_full_member=True,
        participants=[{"name": "Alice Junior", "alias": "Alice Jr"}],
    )
    mem_db["/users/bob@test.com"] = MockUser(
        "bob@test.com",
        alias="Bob",
        is_full_member=False,
    )

    teamup_id = "1616790286-rid-1713420000"
    kc_id = "kc_cal_wrestling_master1_20260907T110000Z"

    # Set check-in entries in kydb under both ID styles
    mem_db[f"/checkins/2026-09-07/{teamup_id}/alice@test.com"] = "checkedin"
    mem_db[f"/checkins/2026-09-07/{kc_id}/bob@test.com"] = "checkedin"

    # Mock _signed_ups and _get_events
    def mock_signed_ups(event_id):
        if event_id == teamup_id:
            return [{"email": "alice@test.com", "participant_id": -1}]
        elif event_id == kc_id:
            return [{"email": "bob@test.com", "participant_id": -1}]
        return []

    h._signed_ups = mock_signed_ups
    h._get_events = lambda start_dt, end_dt: [
        {
            "id": teamup_id,
            "title": "BJJ",
            "subcalendar_id": 9946633,
            "start_dt": "2026-09-07T10:00:00+01:00",
            "end_dt": "2026-09-07T11:00:00+01:00",
        },
        {
            "id": kc_id,
            "title": "Wrestling",
            "subcalendar_id": 11273394,
            "start_dt": "2026-09-07T11:00:00+01:00",
            "end_dt": "2026-09-07T12:00:00+01:00",
        },
    ]

    participants = h._get_participants(
        datetime(2026, 9, 7).date(), datetime(2026, 9, 7).date()
    )
    assert len(participants) == 2

    p_alice = next(p for p in participants if p["user-id"] == "alice@test.com")
    assert p_alice["event_id"] == teamup_id
    assert p_alice["status"] == "checkedin"
    assert p_alice["reward"] == "⭐⭐"
    assert p_alice["icon"] == "person_check"

    p_bob = next(p for p in participants if p["user-id"] == "bob@test.com")
    assert p_bob["event_id"] == kc_id
    assert p_bob["status"] == "checkedin"
    assert p_bob["reward"] == "⭐"
    assert p_bob["icon"] == "person_cancel"  # non-paying member


def test_provider_awareness_selection(monkeypatch):
    """Verify that _is_kakuto routes to Teamup when /configs/timetable is absent or teamup,
    and routes to kakuto when provider is kakuto."""
    # Scenario 1: No /configs/timetable -> Teamup
    db_teamup = kydb.connect("memory://test_teamup")
    h_teamup = lambda_function.Handler(db_teamup, "uat")
    assert not h_teamup._is_kakuto()

    teamup_called = []

    def mock_requests_get(url, headers):
        teamup_called.append(url)

        class MockResp:
            def json(self):
                return {
                    "events": [
                        {
                            "id": "teamup_evt",
                            "start_dt": "2026-09-07T10:00:00",
                            "end_dt": "2026-09-07T11:00:00",
                            "subcalendar_id": 9946633,
                            "title": "BJJ",
                        }
                    ]
                }

        return MockResp()

    monkeypatch.setattr(lambda_function.requests, "get", mock_requests_get)
    events = h_teamup._get_events(
        datetime(2026, 9, 7).date(), datetime(2026, 9, 7).date()
    )
    assert len(teamup_called) == 1
    assert events[0]["id"] == "teamup_evt"

    # Scenario 2: /configs/timetable has provider: 'teamup' -> Teamup
    db_teamup["/configs/timetable"] = {"provider": "teamup"}
    assert not h_teamup._is_kakuto()

    # Scenario 3: /configs/timetable has provider: 'kakuto' -> ak-class-timetable invocation
    db_kakuto = kydb.connect("memory://test_kakuto")
    db_kakuto["/configs/timetable"] = {
        "provider": "kakuto",
        "kakuto": {"calendars": []},
    }
    h_kakuto = lambda_function.Handler(db_kakuto, "uat")
    assert h_kakuto._is_kakuto()

    invocations = []

    class MockLambdaClient:
        def invoke(self, FunctionName, InvocationType, Payload):
            invocations.append(
                {"function": FunctionName, "payload": json.loads(Payload.decode())}
            )
            response_body = {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "events": [
                            {
                                "id": "kc_evt_test_123",
                                "title": "Wrestling",
                                "subcalendar_id": 11273394,
                                "description": "Wrestling",
                                "start_dt": "2026-09-07T18:00:00+01:00",
                                "end_dt": "2026-09-07T19:00:00+01:00",
                            }
                        ]
                    }
                ),
            }

            class MockPayload:
                def read(self):
                    return json.dumps(response_body).encode()

            return {"Payload": MockPayload()}

    monkeypatch.setattr(
        lambda_function.boto3, "client", lambda service: MockLambdaClient()
    )
    events_kc = h_kakuto._get_events(
        datetime(2026, 9, 7).date(), datetime(2026, 9, 7).date()
    )
    assert len(invocations) == 1
    assert (
        invocations[0]["function"]
        == lambda_function.AK_CLASS_TIMETABLE_LAMBDA_MAP["uat"]
    )
    assert invocations[0]["payload"]["method"] == "get_classes"
    assert events_kc[0]["id"] == "kc_evt_test_123"
    assert events_kc[0]["title"] == "Wrestling"


if __name__ == "__main__":
    test_format_cal_event_with_teamup_and_kakuto_ids()
    test_current_and_next_event_resolution()
    test_find_check_in_windows()
    test_get_participants_transparent_ids()
    print("All unit tests passed!")
