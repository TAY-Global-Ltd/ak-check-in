# Example Server

This is just an example server to host it serverlessly.

It assumes that the sign-ups and check-ins are already put into a dynamodb and
that publishing to PubNub is already done.

## Setup

copy ``settings-example.py`` to ``settings.py`` and make appropriate changes.

Create ``.env`` that has the following:

```
export AWS_DEFAULT_REGION=eu-west-2
export TEAMUP_API_KEY=XXXXXXX
export PUB_NUB_SUBSCRIBE_KEY=XXXXXX
```

You'll need to encrypt the value using ``kms_utils.encrypt_secret``.

Then run ``source .env``


Run ``setup.py`` to setup the AWS stack. Note it assumes that the roles and policies already exists.

Go to AWS API gateways and enable CORS for each method. Should really have ``setup.py`` do that, but haven't got around to it.

Run ``make deploy`` to deploy the lambda function.

You should then be able to ``curl`` the URL provided by api gateway.
The base URL is printed when you ran ``setup.py``

