import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from secret_santa import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
logger = logging.getLogger(__name__)


def send_message(message_body: str, recipient_number: str) -> None:
    """
    Thin wrapper around Twilio client to send an SMS message.
    """

    try:
        client.messages.create(
            body=message_body, to=recipient_number, from_=settings.TWILIO_SENDING_NUMBER
        )
    except TwilioRestException:
        logger.exception("🚨🚨🚨 Unable to send Twilio message! 🚨🚨🚨")
        raise
