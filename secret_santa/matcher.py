import logging
from random import choice as randchoice

logger = logging.getLogger(__name__)


def match(recipient_list: list) -> dict:
    """
    Match recipient with secret santas.

    Given a list of strings (could be names or phone numbers, etc), create two identical lists:
        - names (pool of secret santas)
        - recipients (who gets a secret santa)

    Choose a random recipient.
    Choose a random secret santa from a temporary pool excluding the recipient.
    (Important that we create the temporary pool so we DO NOT remove recipient from ongoing secret santa pool!)

    Store the match and remove recipient from recipients list, and secret santa from names list.
    Reset and attempt again if last remaining recipient and secret santa pool is the same person.
    """

    names, recipients = [], []
    matches = {}
    ALL_MATCHED = False

    def setup() -> None:
        nonlocal names, recipients, matches
        matches.clear()
        names = recipient_list
        recipients = names[:]
        # names = ['a', 'b', 'c', 'd']  # uncomment this line for debugging

    setup()

    logger.debug(f"names: {names}")
    logger.debug(f"recipients: {recipients}")

    while not ALL_MATCHED:
        logger.debug("\n\n🎄 ---------- Start matching!!! ---------- 🎄\n\n")

        for _ in range(len(names)):
            recipient = randchoice(recipients)
            logger.debug(f"Finding secret santa for recipient {recipient}")

            without_recipient = names
            if recipient in names:
                without_recipient = (
                    names[: names.index(recipient)] + names[names.index(recipient) + 1 :]
                )

            if not without_recipient:
                logger.debug("Oops! Have to reshuffle!\n")
                setup()
                break

            secret_santa = randchoice(without_recipient)
            names.pop(names.index(secret_santa))
            logger.debug(f"Found match {secret_santa} for recipient {recipient}")

            matches[recipient] = secret_santa

            recipients.pop(recipients.index(recipient))
            logger.debug(f"Remaining recipients are {recipients}")
            logger.debug(f"Remaining secret santas are {names}\n")

        if not recipients and not names:
            ALL_MATCHED = True

    logger.debug(matches)
    return matches
