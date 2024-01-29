# Mock Messages

Used for sending mock messages for testing

## Installation

```
pip install -r requirements.txt
```

## Storing the keys

As a good practice, we're not going to store the in git up.
Even locally we don't want to leave it as plain text.
We're going to encrypt it instead.

Create ``.env`` and put that into in the same directory as this README.
**DO NOT** check this into git. ``.gitigore`` should prevent that anyway.

The content should be:

```
export PUB_NUB_SUBSCRIBE_KEY=the_subscription_key
export PUB_NUB_PUBLISH_KEY=the_pubish_key
```

You can get those keys from your PubNub account and use the below command to encrypt it.

```
python -c "from crypto import encrypt; print(encrypt('My secret key'))"
```


## Running

First make sure the environment variables are setup:

```
source .env
```

They run the script below

```
python send_messages.py
```