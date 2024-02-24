import lambda_function
import kydb
from pprint import pprint
from settings import TABLE_MAP
import requests

stage = "uat"
event = {"requestContext": {"stage": stage}}
db = kydb.connect("dynamodb://" + TABLE_MAP[stage])


def test_current_next_event():
    h = lambda_function.Handler(db, stage)
    events = h.current_event()
    print("[current_event]")
    print("-" * 80)
    pprint(events)

    print("[next_event]")
    print("-" * 80)
    events = h.next_event()
    pprint(events)


def test_initial_state():
    h = lambda_function.Handler(db, stage)
    events = h.initial_state()
    pprint(events)

def test_checkin():
    res = requests.get('https://l6odffk4jd.execute-api.eu-west-2.amazonaws.com/uat/current_event')
    event_id = res.json()['id']
    event = {
        'stage': 'uat',
        'method': 'user_action',
        'kwargs': {
            'event_id': event_id,
            'status': 'checkedin',
            'user_id': 'demo-user@artillerykai.co.uk'
        }
    }
    lambda_function.lambda_handler(event, None)


if __name__ == "__main__":
    # test_initial_state()
    # test_current_next_event()
    test_checkin()
