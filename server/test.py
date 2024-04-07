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

db = kydb.connect("dynamodb://" + TABLE_MAP[stage])


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
            "participant_id": 0
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
    user.additional_participants.setvalue([
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
        }
    ])
    user.write()

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
            "participant_id": 1
        },
    }
    lambda_function.lambda_handler(event, None)

if __name__ == "__main__":
    test_initial_state()
    # test_current_next_event()
    # test_checkin()
    # test_signup()

