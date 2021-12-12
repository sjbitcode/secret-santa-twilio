import argparse
import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

"""
Find your Account SID and Auth Token at twilio.com/console
and set the environment variables. See http://twil.io/secure
"""
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_SENDING_NUMBER")
client = Client(account_sid, auth_token)


def parse_args():
    parser = argparse.ArgumentParser(description="Send a test Twilio message.")
    parser.add_argument(
        "--to",
        type=str,
        required=True,
        help="Phone number to send message to, ex. +1233457891",
        action="store",
    )
    return parser.parse_args()


def send_message(recipient_number: str) -> None:
    message = client.messages.create(
        body="This is the ship that made the Kessel Run in fourteen parsecs?",
        from_=twilio_number,
        media_url=["https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg"],
        to=recipient_number,
    )
    print(message.sid)


if __name__ == "__main__":
    args = parse_args()
    send_message(args.to.strip())
