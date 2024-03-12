"""
This is a script to upload the build folder to S3. It is used by the deploy.sh script.

You'll still need to setup AWS certificate, CloudFront
and have route53 setup to point to the CloudFront distribution.
"""

from datetime import datetime
import subprocess
import sys
import server.settings as settings
import os
import boto3
import time


cf = boto3.client("cloudfront")


def get_distribution_config(stage):
    dist_id = settings.DISTRIBUTION_ID_MAP[stage]
    response = cf.get_distribution_config(Id=dist_id)
    return dist_id, response["DistributionConfig"], response["ETag"]


def create_invalidation(dist_id):
    response = cf.create_invalidation(
        DistributionId=dist_id,
        InvalidationBatch={
            "Paths": {"Quantity": 1, "Items": ["/*"]},
            "CallerReference": str(
                datetime.now()
            ),  # Unique reference for the invalidation
        },
    )

    invalidation_id = response["Invalidation"]["Id"]
    print("Created invalidation with ID:", invalidation_id)
    return invalidation_id


def update_distribution(stage, origin_path):
    dist_id, cfg, etag = get_distribution_config(stage)
    origins = cfg["Origins"]["Items"]
    origin_to_update = origins[0]
    origin_to_update["OriginPath"] = origin_path

    result = cf.update_distribution(DistributionConfig=cfg, Id=dist_id, IfMatch=etag)

    print(result)

    print(f"Updated distribution with ID: {dist_id}, origin path: {origin_path}")
    return dist_id


def wait_for_invalidation_completion(distribution_id, invalidation_id):
    for _i in range(60):
        response = cf.get_invalidation(
            DistributionId=distribution_id, Id=invalidation_id
        )
        status = response["Invalidation"]["Status"]

        if status == "Completed":
            print("Invalidation completed:", invalidation_id)
            break
        else:
            print("Invalidation in progress. Waiting...")
            time.sleep(3)


def upload(stage):
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    bucket = settings.WEBAPP_S3_BUCKET_MAP[stage]
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

    return f'/{dt}'


def build(stage):
    env = os.environ.copy()
    env["REACT_APP_CHECKIN_API_SERVER_URL"] = settings.CHECKIN_API_SERVER_URL_MAP[stage]
    env["PUBLIC_URL"] = settings.PUBLIC_URL_MAP[stage]

    cmd = ["npm", "run", "build"]

    res = subprocess.run(cmd, env=env)

    if res.returncode != 0:
        raise RuntimeError("Build failed")


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage not in settings.DISTRIBUTION_ID_MAP:
        raise ValueError(f"Invalid stage: {stage}")

    build(stage)
    origin_path = upload(stage)
    dist_id = update_distribution(stage, origin_path)
    invalidation_id = create_invalidation(dist_id)
    wait_for_invalidation_completion(dist_id, invalidation_id)
