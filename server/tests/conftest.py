"""Import lambda_function offline: a stub ``settings`` (the real one is
gitignored) and a ``get_secret`` that reads no KMS."""

import os
import sys
import types

SERVER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SERVER)

if "settings" not in sys.modules:
    settings = types.ModuleType("settings")
    settings.SETTINGS = {"timezone": "Europe/London"}
    settings.CAL_BASE_URL = "https://calendar.invalid"
    settings.CAL_EVENT_ICON_BASE_FOLDER = "https://icons.invalid/"
    settings.CAL_EVENT_ICON_MAP = {}
    settings.CAL_EVENT_TITLE = {}
    settings.TIME_ZONE_NAME = "Europe/London"
    settings.PUB_NUB_CHANNEL_MAP = {"uat": "checkin-uat", "prod": "checkin-prod"}
    settings.PUB_NUB_USER_ID = "test-user"
    settings.TABLE_MAP = {"uat": "ak-uat", "prod": "ak-prod"}
    settings.AK_CLASS_TIMETABLE_LAMBDA_MAP = {
        "uat": "ak-class-timetable-uat",
        "prod": "ak-class-timetable",
    }
    settings.KMS_ID_KEY = "test"
    sys.modules["settings"] = settings

import lib  # noqa: E402  (server/lib, a namespace package)

kms_utils = types.ModuleType("lib.kms_utils")
kms_utils.get_secret = lambda name: "test-" + name.lower()
sys.modules["lib.kms_utils"] = kms_utils
lib.kms_utils = kms_utils
