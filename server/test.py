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
    h = lambda_function.Handler(db, stage)
    events = h.initial_state()
    pprint(events)


def test_initial_state():
    event = {
        "path": "/initial_state",
        "requestContext": {
            "stage": "uat",
        },
        "headers": {"AUTHORIZATION": "Bearer MY_DUMMY_TOKEN"},
    }

    res = lambda_function.lambda_handler(event, None)
    body = json.loads(res["body"])
    expected = {"settings", "subscription_info", "attendees"}
    assert set(body.keys()) == expected

    event["headers"]["AUTHORIZATION"] = "Bearer BAD_TOKEN"

    with pytest.raises(lambda_function.AuthorizationError):
        lambda_function.lambda_handler(event, None)


def test_checkin():
    res = requests.get(
        "https://l6odffk4jd.execute-api.eu-west-2.amazonaws.com/uat/current_event"
    )
    event_id = res.json()["id"]
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


if __name__ == "__main__":
    test_initial_state()
    # test_current_next_event()
    # test_checkin()
