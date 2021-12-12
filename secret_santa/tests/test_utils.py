import unittest
from unittest.mock import patch

from twilio.base.exceptions import TwilioRestException

from secret_santa import utils

TWILIO_SENDING_NUMBER = "+1111111111"
ALICE_NUMBER = "+1234567891"


@patch("secret_santa.settings.TWILIO_ACCOUNT_SID", "test-twilio-account-sid")
@patch("secret_santa.settings.TWILIO_AUTH_TOKEN", "test-twilio-auth-token")
@patch("secret_santa.settings.TWILIO_SENDING_NUMBER", TWILIO_SENDING_NUMBER)
class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.mock_client_create = patch.object(
            utils.client.messages, "create", autospec=True
        ).start()
        self.addCleanup(patch.stopall)

    def test_send_message(self):
        utils.send_message(message_body="Howdy!", recipient_number=ALICE_NUMBER)

        self.mock_client_create.assert_called_once_with(
            body="Howdy!", to=ALICE_NUMBER, from_=TWILIO_SENDING_NUMBER
        )

    @patch("secret_santa.utils.logger")
    def test_send_message_logs_and_raises_exception(self, mock_logger):
        self.mock_client_create.side_effect = TwilioRestException(400, "twilio/post/endpoint")

        with self.assertRaises(TwilioRestException):
            utils.send_message(message_body="Howdy!", recipient_number=ALICE_NUMBER)

        self.mock_client_create.assert_called_once_with(
            body="Howdy!", to=ALICE_NUMBER, from_=TWILIO_SENDING_NUMBER
        )
        mock_logger.exception.assert_called_with("🚨🚨🚨 Unable to send Twilio message! 🚨🚨🚨")
