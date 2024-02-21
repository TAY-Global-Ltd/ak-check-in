# Example Server

This is just an example server to host it serverlessly.

It assumes that the sign-ups and check-ins are already put into a dynamodb and
that publishing to PubNub is already done.

## Setup

 * copy ``settings-example.py`` to ``settings.py`` and make appropriate changes.
 * Create ``.env`` that has the following variables: ``AWS_DEFAULT_REGION`` and ``TEAMUP_API_KEY``