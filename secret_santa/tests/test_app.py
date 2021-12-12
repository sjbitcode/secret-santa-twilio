import unittest
from unittest.mock import create_autospec, patch

from twilio.base.exceptions import TwilioRestException

from secret_santa import manager
from secret_santa.app import create_app


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.mock_logger = patch("secret_santa.app.logger").start()
        patch("secret_santa.settings.get_recipients").start()

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["DEBUG"] = False
        self.app.config["game"] = create_autospec(manager.Game)
        self.client = self.app.test_client()

        self.addCleanup(patch.stopall)

    def test_get_method_not_supported(self):
        response = self.client.get("/sms")

        self.assertEqual(response.status_code, 405)

    def test_successful_response(self):
        response = self.client.post("/sms", data={"Body": "Howdy!", "From": "+1234567891"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "<Response></Response>")
        self.app.config["game"].handle_message.assert_called_once_with("Howdy!", "+1234567891")

    def test_handle_message_raises_twilio_exception(self):
        self.app.config["game"].handle_message.side_effect = TwilioRestException(
            400, "twilio/post/endpoint"
        )

        response = self.client.post("/sms", data={"Body": "Howdy!", "From": "+1234567891"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_data(as_text=True), "Encountered Twilio error")
        self.mock_logger.exception.assert_called_with("There was an error with Twilio! ‼️")
