import lambda_function
import kydb
from pprint import pprint
from settings import TABLE_MAP

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


if __name__ == "__main__":
    test_initial_state()
    test_current_next_event()
