import boto3
import os
import base64
from settings import KMS_ID_KEY


def encrypt_secret(secret):
    kms = boto3.client("kms")
    res = kms.encrypt(KeyId=KMS_ID_KEY, Plaintext=secret)
    return base64.b64encode(res["CiphertextBlob"])


def get_secret(name):
    kms = boto3.client("kms")
    encrypted = os.environ[name]
    res = kms.decrypt(KeyId=KMS_ID_KEY, CiphertextBlob=base64.b64decode(encrypted))

    return res["Plaintext"].decode()
