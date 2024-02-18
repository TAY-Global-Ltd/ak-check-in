from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from fastapi import FastAPI
import uvicorn
from typing import Optional
import json
from crypto import get_secret
from send_messages import MockSubscribeCallback
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

CHANNEL = "dev-checkin"
SUBSCRIBE_KEY = get_secret('PUB_NUB_SUBSCRIBE_KEY')
PUBLISH_KEY = get_secret('PUB_NUB_PUBLISH_KEY')
USER_ID = "my_custom_user_id"

app = FastAPI()

origins = [
    "http://192.168.1.105:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fixture: Optional[dict] = None
message_history = []


@app.get("/event")
def event(event_id: str):
    return next(x for x in fixture['events'] if x['id'] == event_id)


@app.get("/current_event")
def current_event():
    return fixture['events'][0]


@app.get("/next_event")
def next_event():
    return fixture['events'][1]


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/initial_state")
def initial_state():
    return {
        "subscription_info": {
            "subscribe_key": SUBSCRIBE_KEY,
            "user_id": USER_ID,
            "channel": CHANNEL,
        },
        "current_event": fixture['events'][0],
        "next_event": fixture['events'][1],
        "attendees": fixture['initial_state'] + message_history,
    }


if __name__ == "__main__":
    fixture_name = "mock_fixture1"

    with open(fixture_name + ".json", "r") as f:
        fixture = json.load(f)

    pnconfig = PNConfiguration()

    pnconfig.subscribe_key = SUBSCRIBE_KEY
    pnconfig.publish_key = PUBLISH_KEY
    pnconfig.user_id = USER_ID

    pubnub = PubNub(pnconfig)

    mock_sub = MockSubscribeCallback(
        fixture=fixture, message_history=message_history)
    pubnub.add_listener(mock_sub)
    pubnub.subscribe().channels(CHANNEL).execute()

    uvicorn.run(app, host="0.0.0.0", port=8765)
