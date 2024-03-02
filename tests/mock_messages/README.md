# Mock Messages

Used for mock HTTP Restful server as well as sending mock messages to PubNub for testing.

## Installation

```
pip install -r requirements.txt
```

## Storing the keys

As a good practice, we're not going to store the in GitHub.
Even locally we don't want to leave it as plain text.
We're going to encrypt it instead.

Create ``.env`` and put that into in the same directory as this README.
**DO NOT** check this into git. ``.gitigore`` should prevent that anyway.

The content should be:

```
export PUB_NUB_SUBSCRIBE_KEY=the_encrypted_subscription_key
export PUB_NUB_PUBLISH_KEY=the_encrypted_pubish_key
export AUTHORIZATION_TOKEN=the_encrypted_auth_token
``` 

You can get those keys from your PubNub account and use the below command to encrypt it.

```
python -c "from crypto import encrypt; print(encrypt('My secret key'))"
```

Note: this is only for a our mock server. In production we'll recommend that you encrypt it using AWS KMS,
Vault or other services where there are key rotation and other more advanced security.

## Running

First make sure the environment variables are setup:

```
source .env
```

They run the script below

```
python mock_server.py
```

### Initial State

To get the initial state. This represent the current state of the screen used when the UI first initialises. 

Make sure to replace ``MY_DUMMY_TOKEN`` with your token encrypted in ``.env``

```
curl -H "Content-Type: application/json" -H "Authorization: Bearer MY_DUMMY_TOKEN" http://127.0.0.1:8765/initial_state 
```

Example output: 

```
{"settings":{"theme":"default","display_mode":"dark","refresh_interval":3600,"title":"My Martial Arts Academy","description":"Welcome to our academy! We offer a variety of martial arts classes. Please check in to earn rewards!","icon":"http://localhost:8765/static/images/logo.png","timezone":"Europe/London"},"subscription_info":{"subscribe_key":"sub-c-08cc7ea1-02ad-4c5d-8b44-5325568e63a7","user_id":"my_custom_user_id","channel":"dev-checkin"},"current_event":{"id":"event-1","title":"BJJ","description":"BJJ Fundamentals","start_time":"18:00","end_time":"19:30","icon":"http://localhost:8765/static/images/bjj.png","icon_type":"url"},"next_event":{"id":"event-2","title":"Muay Thai","description":"Muay Thai","start_time":"19:30","end_time":"21:00","icon":"http://localhost:8765/static/images/muaythai.png","icon_type":"url"},"attendees":[{"event_id":"event-1","user-id":"user0003","name":"John Smith","icon":"person_check","icon_type":"material","reward":"⭐","status":"checkedin"},{"event_id":"event-1","user-id":"user0004","name":"Peter Parker","icon":"person_check","icon_type":"material","reward":"","status":"signedup"},{"event_id":"event-1","user-id":"user0005","name":"Uzumaki Naruto","icon":"person","icon_type":"material","reward":"","status":"checkedin"}]}
```

The settings are as follows:

* ``display_modeb``: ``dark`` or ``light``.
* ``refresh_interval``: Number of seconds until the page should refresh itself.
* ``title``: Set the title of the page
* ``description``: Set the description of the page
* ``icon``: The icon for the webapp
* ``timezone``: The timezone of the gym. For example ``Europe/London``

### Get Current Event

To get the event of the current class

```
curl -H "Content-Type: application/json" -H "Authorization: Bearer MY_DUMMY_TOKEN" http://127.0.0.1:8765/current_event
```

Example Output:

```
{
  "id": "event-1",
  "title": "BJJ",
  "description": "BJJ Fundamentals",
  "start_time": "18:00",
  "end_time": "19:30",
  "icon_type": "url",
  "icon": "http://127.0.0.1:8765/static/images/bjj.png"
}
```

Notice the ``icon_type`` is ``url`` so the icon is a valid URL where the icon is served.
You can go ahead and open the below URL to see the icon.

http://127.0.0.1:8765/static/images/bjj.png

### Get Next Event

To get the event of the current class

```
curl -H "Content-Type: application/json" -H "Authorization: Bearer MY_DUMMY_TOKEN" http://127.0.0.1:8765/next_event
```

Example Output:

```
{
  "id": "event-2",
  "title": "Muay Thai",
  "description": "Muay Thai",
  "start_time": "19:30",
  "end_time": "21:00",
  "icon": "http://127.0.0.1:8765/static/images/muaythai.png",
  "icon_type": "url"
}
```

## Schema

Both initial state and messages sent to PubNub topic looks like this

  * event_id - The event id of the class which can be requested for more details from the request server
  * user-id - A unique user id which should not be email address or anything that would give away confidential information about the real person.
  * name - The name of the member, but should be an alias that the user has agree to display. Could just be a first name or some other nick name.
  * icon - The icon to be displayed. The value would depend on icon_type
  * icon_type - The icon type, it can take the following values: ``url``, ``material`` or ``internal``
  * reward - The club can give rewards like most number of classes attended etc... typically this is a set of emojis.
  * status - It can take the following values:
    * signedup - User has signed up on the app but not physically at the gym
    * checkedin - User has checked in at the gym
    * cancelled - User has cancelled their signup up which can be done on the app. But once check in has happened user cannot cancel that.

