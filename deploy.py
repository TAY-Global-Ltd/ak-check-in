"""
This is a script to upload the build folder to S3. It is used by the deploy.sh script.

You'll still need to setup AWS certificate, CloudFront
and have route53 setup to point to the CloudFront distribution.
"""

from datetime import datetime
import subprocess
import sys
from server.settings import (
    CHECKIN_API_SERVER_URL_MAP,
    PUBLIC_URL_MAP,
    WEBAPP_S3_BUCKET_MAP,
)
import os


def upload(stage):
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    bucket = WEBAPP_S3_BUCKET_MAP[stage]
    s3_folder = f"s3://{bucket}/{dt}/"
    cmd = [
        "aws",
        "s3",
        "sync",
        "build",
        s3_folder,
        "--acl",
        "public-read",
    ]
    print(f"Uploading to {s3_folder}")

    if subprocess.call(cmd):
        raise RuntimeError("Cannot upload to S3")


def build(stage):
    env = os.environ.copy()
    env["REACT_APP_CHECKIN_API_SERVER_URL"] = CHECKIN_API_SERVER_URL_MAP[stage]
    env["PUBLIC_URL"] = PUBLIC_URL_MAP[stage]

    cmd = ["npm", "run", "build"]

    res = subprocess.run(cmd, env=env)

    if res.returncode != 0:
        raise RuntimeError("Build failed")


if __name__ == "__main__":
    stage = sys.argv[1]
    build(stage)
    if stage in WEBAPP_S3_BUCKET_MAP:
        upload(stage)
