# Copy this to settings.py
#
# TODO: Put this in a yaml config
# or even better cloud formation or terra form

TIME_ZONE_NAME = "Europe/London"

APP_NAME = 'ak-check-in'
AWS_REGION = 'eu-west-2'

ROLE_NAME = 'ak-check-in-lambda'

TABLE_MAP = {
    'dev': 'ak-check-in-uat',
    'uat': 'ak-check-in-uat',
    'prod': 'ak-check-in-prod'
}

LAMBDA_FUNCTION_MAP = {
    'dev': 'ak-check-in-uat',
    'uat': 'ak-check-in-uat',
    'prod': 'ak-check-in-prod'
}

AWS_ACCOUNT=652040406068

API_GATEWAY_MAP = {
    'uat': 'ak-check-in-uat',
    'prod': 'ak-check-in-prod'
}

KMS_ID_KEY = 'XXXXX'

CAL_BASE_URL = "https://api.teamup.com/[calendaer_id]"

CAL_EVENT_ICON_BASE_FOLDER = 'https://my.image-server.com/images/ak-check-in/class-type-logos/'

CAL_EVENT_ICON_MAP = {
    1234: 'yoga.png',
    2345: 'bjj.png',
    3456: 'muaythai.png',
    4567: 'running.png',
    5678: 'mma.png',
}