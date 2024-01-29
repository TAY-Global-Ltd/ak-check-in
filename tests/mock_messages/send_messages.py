from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from threading import Thread
from typing import Optional
from time import sleep
import json
from crypto import get_secret


def mock_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if status.is_error():
        print("ERROR: ", status.original_response)


class MockSubscribeCallback(SubscribeCallback):
    def __init__(self, *args, **kwargs):
        fixture_name = kwargs.pop("fixture_name")
        interval = kwargs.pop("interval")
        super().__init__(*args, **kwargs)
        self.publish_thread: Optional[Thread] = None
        with open(fixture_name + ".json", "r") as f:
            self.fixture = json.load(f)
        self.interval = interval

        self.pubnub = None

    def presence(self, pubnub, presence):
        print("presence")
        print(pubnub)
        print(presence)

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("Unexpected disconnection.")

        elif status.category == PNStatusCategory.PNConnectedCategory and not self.publish_thread:
            self.pubnub = pubnub
            self.publish_thread = Thread(target=self.publish_loop)
            self.publish_thread.start()

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Reconnected")
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            print("Decryption Error")

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        print(f"Received message: {message.message}")

    def publish_loop(self):
        for member in self.fixture:
            self.pubnub.publish().channel(
                'dev-checkin').message(member).pn_async(mock_publish_callback)
            sleep(self.interval)


if __name__ == '__main__':
    pnconfig = PNConfiguration()

    pnconfig.subscribe_key = get_secret('PUB_NUB_SUBSCRIBE_KEY')
    pnconfig.publish_key = get_secret('PUB_NUB_PUBLISH_KEY')
    pnconfig.user_id = "my_custom_user_id"

    pubnub = PubNub(pnconfig)

    mock_sub = MockSubscribeCallback(fixture_name='mock_fixture1', interval=5)
    pubnub.add_listener(mock_sub)
    pubnub.subscribe().channels('dev-checkin').execute()
