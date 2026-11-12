"""F3 (health audit 2026-11-12): ak-check-in-prod raised
``KeyError: '/users/<email>'`` in ``user_action`` for every member of a gym
other than the default one (291/1,120 invocations, 97 async events dropped).

These tests replay the event ak-class-timetable's ``_notify_checkins`` sends
(``gym_id`` at the top level, not in ``kwargs``) for every configured gym and
check the member is read from that gym's store and reaches the feed, and that
nothing the async invoke would retry is raised.
"""

import os
import re
import uuid

import kydb
import pytest

import lambda_function
from lambda_function import DEFAULT_GYM_ID, GYM_DB_SUFFIX

from test_user_action import FakePubNub, FakeUser, published

OTHER_GYMS = sorted(g for g in GYM_DB_SUFFIX if g != DEFAULT_GYM_ID)


@pytest.fixture
def pubnub(monkeypatch):
    fake = FakePubNub()
    monkeypatch.setattr(lambda_function, "pubnub", fake)
    return fake


@pytest.fixture
def connect(monkeypatch):
    name = str(uuid.uuid4())
    opened = []

    def connect(url):
        opened.append(url)
        return kydb.connect(url.replace("dynamodb://", f"memory://{name}-"))

    connect.opened = opened
    monkeypatch.setattr(lambda_function, "_connect_db", connect)
    return connect


def notify_event(stage, gym_id, status, user_id, participant_id=-1):
    """The invoke event of ak-class-timetable ``_notify_checkins``."""
    return {
        "stage": stage,
        "method": "user_action",
        "gym_id": gym_id,
        "kwargs": {
            "event_id": "evt-1",
            "status": status,
            "user_id": user_id,
            "participant_id": participant_id,
        },
    }


def test_the_prod_failure_is_reproduced_without_gym_routing(connect, pubnub):
    """The pre-fix lookup (root store only) raises the prod KeyError for a
    member who exists only in their gym's store."""
    gym = connect("dynamodb://ak-prod/diesel_gym")
    gym["/users/m@example.com"] = FakeUser("m@example.com", "Mo")
    root = connect("dynamodb://ak-prod")
    with pytest.raises(KeyError, match="/users/m@example.com"):
        root["/users/m@example.com"]


@pytest.mark.parametrize("stage", ["uat", "prod"])
@pytest.mark.parametrize("gym_id", OTHER_GYMS)
@pytest.mark.parametrize("status", ["signedup", "checkedin", "cancelled"])
def test_every_gym_reaches_the_feed(connect, pubnub, stage, gym_id, status):
    table = lambda_function.TABLE_MAP[stage]
    gym = connect(f"dynamodb://{table}/{gym_id}")
    gym["/users/m@example.com"] = FakeUser("m@example.com", "Mo")
    gym["/rewards/stars"] = {"m@example.com": 3}
    connect.opened.clear()

    res = lambda_function.lambda_handler(
        notify_event(stage, gym_id, status, "m@example.com"), None
    )

    assert res["statusCode"] == 200
    [(channel, msg)] = published(pubnub)
    assert channel == lambda_function.PUB_NUB_CHANNEL_MAP[stage]
    assert msg["user-id"] == "m@example.com"
    assert msg["name"] == "Mo"
    assert msg["status"] == status
    assert msg["reward"] == "⭐⭐⭐"
    assert f"dynamodb://{table}/{gym_id}" in connect.opened


def test_old_timetable_without_gym_id_uses_the_default_store(connect, pubnub):
    root = connect("dynamodb://ak-prod")
    root["/users/a@example.com"] = FakeUser("a@example.com", "Alice")
    event = notify_event("prod", None, "checkedin", "a@example.com")
    del event["gym_id"]
    assert lambda_function.lambda_handler(event, None)["statusCode"] == 200
    [(_, msg)] = published(pubnub)
    assert msg["name"] == "Alice"


def test_default_gym_id_uses_the_root_store(connect, pubnub):
    root = connect("dynamodb://ak-prod")
    root["/users/a@example.com"] = FakeUser("a@example.com", "Alice")
    connect.opened.clear()
    lambda_function.lambda_handler(
        notify_event("prod", DEFAULT_GYM_ID, "signedup", "a@example.com"), None
    )
    [(_, msg)] = published(pubnub)
    assert msg["name"] == "Alice"
    assert connect.opened == ["dynamodb://ak-prod"]  # the handler's own db only


def test_gym_store_is_opened_once_per_invocation(connect, pubnub):
    gym = connect("dynamodb://ak-prod/diesel_gym")
    gym["/users/m@example.com"] = FakeUser("m@example.com", "Mo")
    h = lambda_function.Handler(connect("dynamodb://ak-prod"), "prod", connect=connect)
    connect.opened.clear()
    for status in ("signedup", "checkedin"):
        h.user_action("evt-1", status, "m@example.com", gym_id="diesel_gym")
    assert connect.opened == ["dynamodb://ak-prod/diesel_gym"]


@pytest.mark.parametrize(
    "gym_id", ["diesel_gym", "kakuto_demo", "no_such_gym", DEFAULT_GYM_ID]
)
def test_unresolvable_member_never_raises(connect, pubnub, caplog, gym_id):
    """Anything raised is retried twice by the async invoke and then dropped
    (the 97 AsyncEventsDropped): a member that cannot be found is a WARNING."""
    res = lambda_function.lambda_handler(
        notify_event("prod", gym_id, "checkedin", "gone@example.com"), None
    )
    assert res["statusCode"] == 200
    assert pubnub.messages == []
    assert any(
        r.levelname == "WARNING" and "gone@example.com" in r.getMessage()
        for r in caplog.records
    )


def test_suffixes_follow_the_ak_server_convention():
    assert GYM_DB_SUFFIX[DEFAULT_GYM_ID] == ""
    for gym_id in OTHER_GYMS:
        assert GYM_DB_SUFFIX[gym_id] == "/" + gym_id
    assert "kakuto_demo" in GYM_DB_SUFFIX


def _ak_server_db_suffix(path):
    src = open(path).read()
    block = re.search(r"^DB_SUFFIX = \{(.*?)^\}", src, re.S | re.M).group(1)
    ids = re.findall(r'^\s*"([a-z0-9_]+)":\s*"(/[a-z0-9_]+)"', block, re.M)
    return {DEFAULT_GYM_ID: "", **dict(ids)}


@pytest.mark.skipif(
    not os.environ.get("AK_SERVER_DIR"),
    reason="set AK_SERVER_DIR to an ak-server checkout to compare gym maps",
)
def test_gym_map_matches_ak_server():
    path = os.path.join(os.environ["AK_SERVER_DIR"], "lib", "lambda", "gym_config.py")
    assert GYM_DB_SUFFIX == _ak_server_db_suffix(path)
