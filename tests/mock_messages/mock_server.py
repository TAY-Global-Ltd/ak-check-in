from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from fastapi import FastAPI, Request
import uvicorn
from typing import Optional
import json
from crypto import get_secret
from send_messages import MockSubscribeCallback
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys

CHANNEL = "dev-checkin"
SUBSCRIBE_KEY = get_secret("PUB_NUB_SUBSCRIBE_KEY")
PUBLISH_KEY = get_secret("PUB_NUB_PUBLISH_KEY")
USER_ID = "my_custom_user_id"
AUTHORIZATION_TOKEN = get_secret("AUTHORIZATION_TOKEN")


class AuthenticationException(Exception):
    pass


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

fixture: Optional[dict] = None
message_history = []


def check_auth(func):
    def wrapper(request: Request):
        err = _check_auth(request)
        if err:
            return err

        return func(request)

    return wrapper


@app.get("/current_event")
@check_auth
def current_event(request: Request):
    return fixture["events"][0]


@app.get("/next_event")
@check_auth
def next_event(request: Request):
    return fixture["events"][1]


app.mount("/static", StaticFiles(directory="static"), name="static")


def _check_auth(request: Request):
    auth = request.headers.get("Authorization")
    auth_type, token = auth.split(" ")

    if auth_type != "Bearer" or token != AUTHORIZATION_TOKEN:
        return {"error": "Unauthorized"}


@app.get("/initial_state")
@check_auth
def initial_state(request: Request):
    return {
        "settings": fixture["settings"],
        "subscription_info": {
            "subscribe_key": SUBSCRIBE_KEY,
            "user_id": USER_ID,
            "channel": CHANNEL,
        },
        "current_event": fixture["events"][0],
        "next_event": fixture["events"][1],
        "attendees": fixture["initial_state"] + message_history,
    }


if __name__ == "__main__":
    fixture_name = "mock_fixture1"

    with open(fixture_name + ".json", "r") as f:
        fixture = json.load(f)

    if len(sys.argv) <= 1 or sys.argv[1] != "--request-only":
        pnconfig = PNConfiguration()

        pnconfig.subscribe_key = SUBSCRIBE_KEY
        pnconfig.publish_key = PUBLISH_KEY
        pnconfig.user_id = USER_ID

        pubnub = PubNub(pnconfig)

        mock_sub = MockSubscribeCallback(
            fixture=fixture, message_history=message_history
        )
        pubnub.add_listener(mock_sub)
        pubnub.subscribe().channels(CHANNEL).execute()

    uvicorn.run(app, host="0.0.0.0", port=8765)
