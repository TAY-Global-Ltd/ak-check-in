"""user_action reads the member from their gym's store (gym_id from
ak-class-timetable) and skips, with a WARNING, a user it cannot find."""

import logging
import uuid

import kydb
import pytest

import lambda_function
from lambda_function import Handler


class FakeUser:
    def __init__(self, email, alias, participants=(), full_member=True):
        self._email = email
        self._alias = alias
        self._participants = list(participants)
        self._full = full_member

    def email(self):
        return self._email

    def alias(self):
        return self._alias

    def additional_participants(self):
        return self._participants

    def is_full_member(self):
        return self._full


class FakePubNub:
    def __init__(self):
        self.messages = []

    def publish(self):
        return self

    def channel(self, name):
        self._channel = name
        return self

    def message(self, message):
        self.messages.append((self._channel, message))
        return self

    def sync(self):
        return type("Envelope", (), {"result": type("R", (), {"timetoken": 1})()})()


@pytest.fixture
def pubnub(monkeypatch):
    fake = FakePubNub()
    monkeypatch.setattr(lambda_function, "pubnub", fake)
    return fake


@pytest.fixture
def stores(monkeypatch):
    """One in-memory table per stage URL, shared by every gym prefix."""
    name = str(uuid.uuid4())
    opened = []

    def connect(url):
        opened.append(url)
        return kydb.connect(url.replace("dynamodb://", f"memory://{name}-"))

    monkeypatch.setattr(lambda_function, "_connect_db", connect)
    root = connect("dynamodb://ak-prod")
    opened.clear()
    return root, connect, opened


def make_handler(stores):
    root, connect, _ = stores
    return Handler(root, "prod", connect=connect)


def published(pubnub):
    # user_action publishes each message exactly once (the live 2026-10-10
    # fix); callers unpack a one-item list, so a second publish fails them.
    return list(pubnub.messages)


def test_default_gym_reads_the_root_store(stores, pubnub):
    root, _, opened = stores
    root["/users/a@example.com"] = FakeUser("a@example.com", "Alice")
    root["/rewards/stars"] = {"a@example.com": 2}
    make_handler(stores).user_action("e1", "signedup", "a@example.com")
    [(channel, msg)] = published(pubnub)
    assert channel == "checkin-prod"
    assert msg["user-id"] == "a@example.com"
    assert msg["name"] == "Alice"
    assert msg["reward"] == "⭐⭐"
    assert opened == []


def test_other_gym_reads_that_gyms_store(stores, pubnub):
    root, connect, opened = stores
    gym = connect("dynamodb://ak-prod/diesel_gym")
    gym["/users/b@example.com"] = FakeUser("b@example.com", "Bob")
    gym["/rewards/stars"] = {"b@example.com": 1}
    opened.clear()

    h = make_handler(stores)
    h.user_action("e1", "checkedin", "b@example.com", gym_id="diesel_gym")
    [(_, msg)] = published(pubnub)
    assert msg["name"] == "Bob"
    assert msg["status"] == "checkedin"
    assert msg["reward"] == "⭐"
    assert opened == ["dynamodb://ak-prod/diesel_gym"]
    assert not root.exists("/users/b@example.com")


def test_other_gym_additional_participant(stores, pubnub):
    _, connect, _ = stores
    gym = connect("dynamodb://ak-prod/diesel_gym")
    gym["/users/p@example.com"] = FakeUser(
        "p@example.com", "Parent", participants=[{"alias": "Kid"}]
    )
    make_handler(stores).user_action(
        "e1", "signedup", "p@example.com", 0, gym_id="diesel_gym"
    )
    [(_, msg)] = published(pubnub)
    assert msg["user-id"] == "p@example.com!0"
    assert msg["name"] == "Kid"
    assert msg["parent_name"] == "Parent"
    assert msg["reward"] == ""  # no /rewards/stars in that gym


def test_missing_user_logs_warning_and_skips(stores, pubnub, caplog):
    caplog.set_level(logging.WARNING)
    h = make_handler(stores)
    assert (
        h.user_action("e1", "signedup", "nobody@example.com", gym_id="diesel_gym")
        is None
    )
    assert pubnub.messages == []
    [rec] = [r for r in caplog.records if "nobody@example.com" in r.getMessage()]
    assert rec.levelno == logging.WARNING
    assert "diesel_gym" in rec.getMessage()


def test_missing_user_in_default_gym_skips(stores, pubnub, caplog):
    caplog.set_level(logging.WARNING)
    assert make_handler(stores).user_action("e1", "signedup", "x@example.com") is None
    assert pubnub.messages == []
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_unknown_gym_logs_warning_and_skips(stores, pubnub, caplog):
    root, _, opened = stores
    root["/users/a@example.com"] = FakeUser("a@example.com", "Alice")
    caplog.set_level(logging.WARNING)
    h = make_handler(stores)
    assert (
        h.user_action("e1", "signedup", "a@example.com", gym_id="no_such_gym") is None
    )
    assert pubnub.messages == []
    assert opened == []
    assert any("no_such_gym" in r.getMessage() for r in caplog.records)


def test_lambda_handler_passes_gym_id_to_user_action(stores, pubnub, monkeypatch):
    _, connect, _ = stores
    gym = connect("dynamodb://ak-prod/diesel_gym_tokyo")
    gym["/users/t@example.com"] = FakeUser("t@example.com", "Taro")
    event = {
        "stage": "prod",
        "method": "user_action",
        "gym_id": "diesel_gym_tokyo",
        "kwargs": {
            "event_id": "e1",
            "status": "signedup",
            "user_id": "t@example.com",
            "participant_id": -1,
            "gym_id": "diesel_gym_tokyo",
        },
    }
    res = lambda_function.lambda_handler(event, None)
    assert res["statusCode"] == 200
    [(_, msg)] = published(pubnub)
    assert msg["name"] == "Taro"


def test_lambda_handler_takes_a_top_level_gym_id(stores, pubnub):
    _, connect, _ = stores
    gym = connect("dynamodb://ak-prod/diesel_gym")
    gym["/users/b@example.com"] = FakeUser("b@example.com", "Bob")
    event = {
        "stage": "prod",
        "method": "user_action",
        "gym_id": "diesel_gym",
        "kwargs": {"event_id": "e1", "status": "cancelled", "user_id": "b@example.com"},
    }
    lambda_function.lambda_handler(event, None)
    [(_, msg)] = published(pubnub)
    assert msg["name"] == "Bob"
    assert msg["status"] == "cancelled"


def test_lambda_handler_missing_user_does_not_raise(stores, pubnub):
    event = {
        "stage": "prod",
        "method": "user_action",
        "kwargs": {
            "event_id": "e1",
            "status": "signedup",
            "user_id": "gone@example.com",
            "gym_id": "diesel_gym",
        },
    }
    res = lambda_function.lambda_handler(event, None)
    assert res["statusCode"] == 200
    assert pubnub.messages == []
