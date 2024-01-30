from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from threading import Thread
from typing import Optional
from time import sleep


def mock_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if status.is_error():
        print("ERROR: ", status.original_response)


class MockSubscribeCallback(SubscribeCallback):
    def __init__(self, *args, **kwargs):
        self.fixture = kwargs.pop("fixture")
        self.message_history = kwargs.pop("message_history")

        super().__init__(*args, **kwargs)
        self.publish_thread: Optional[Thread] = None
        self.interval = self.fixture['message_settings']['interval']

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
        self.message_history.append(message.message)

    def publish_loop(self):
        for member in self.fixture['messages']:
            self.pubnub.publish().channel(
                'dev-checkin').message(member).pn_async(mock_publish_callback)
            sleep(self.interval)
