# Copy this to settings.py
#
# TODO: Put this in a yaml config
# or even better cloud formation or terra form

TIME_ZONE_NAME = "Europe/London"

SETTINGS = {
    "theme": "default",
    "display_mode": "dark",
    "refresh_interval": 3600,
    "title": "My Martial Arts Academy",
    "description": "Welcome to our academy! We offer a variety of martial arts classes. Please check in to earn rewards!",
    "icon": "http://my-check-in-app.com/static/images/logo.png",
    "timezone": TIME_ZONE_NAME
}

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

AK_CLASS_TIMETABLE_LAMBDA_MAP = {
    "prod": "ak-class-timetable",
    "uat": "ak-class-timetable-uat",
}

AWS_ACCOUNT=123456789

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

CAL_EVENT_TITLE = {
    1234: 'Yoga',
    2345: 'BJJ',
    3456: 'Muay Thai',
    4567: 'Run Club',
    5678: 'MMA',
}

PUB_NUB_CHANNEL_MAP = {
    "dev": 'checkin-dev',
    "uat": 'checkin-uat',
    "prod": 'checkin-prod',
}

PUB_NUB_USER_ID = "my_custom_user_id"

WEBAPP_S3_BUCKET = "s3.myapp.com"

WEBAPP_S3_BUCKET_MAP = {
    'dev': "my-app-dev-bucket",
    'uat': "my-app-uat-bucket",
    'prod': "my-app-bucket",
}

CHECKIN_API_SERVER_URL_MAP = {
    "dev": "https://api-dev.my-app.com/",
    "uat": "https://api-uat.my-app.com/",
    "prod": "https://api.my-app.com/",
}

PUBLIC_URL_MAP = {
    "dev": "https://dev.my-app.com/",
    "uat": "https://uat.my-app.com/",
    "prod": "https://my-app.com/",
}

DISTRIBUTION_ID_MAP = {
    "dev": "DISTABCDE123",
    "uat": "DISTABCDE456",
    "prod": "DISTABCDE789",
}