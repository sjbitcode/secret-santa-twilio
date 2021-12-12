import csv
import logging
import os
from distutils.util import strtobool
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent.parent
DEBUG = bool(strtobool(os.getenv("DEBUG", "False")))
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SENDING_NUMBER = os.getenv("TWILIO_SENDING_NUMBER")
DOLLAR_BUDGET = int(os.getenv("DOLLAR_BUDGET", "30"))
START_TRIGGER = "start123"
CSV_FILE = BASE_DIR / "numbers.csv"
RECIPIENT_DICT = {}


def load_recipients() -> None:
    """
    Store recipients from numbers.csv file.
    """

    with open(CSV_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name, number = row["name"], row["number"]
            RECIPIENT_DICT[number] = name

    assert len(RECIPIENT_DICT) > 1, "Must have more two or more Secret Santa recipients!"


def get_recipients() -> dict:
    """
    Easy utility method to get recipients.
    """

    if not RECIPIENT_DICT:
        load_recipients()

    return RECIPIENT_DICT


def setup() -> None:
    """
    Configure logging and set recipients. Should be run right before server started.
    """

    logging.basicConfig(level=LOG_LEVEL)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    load_recipients()
