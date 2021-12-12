import concurrent.futures
import logging

from secret_santa import matcher, settings, utils

logger = logging.getLogger(__name__)


class Game:
    """
    A class to start and manage the Secret Santa game state.
    """

    STARTED = False
    WISHLIST = {}

    def __init__(self, recipients: dict, start_trigger: str):
        self.recipients = recipients
        self.start_trigger = start_trigger

    def __repr__(self) -> str:
        return f"Game({self.recipients}, {self.start_trigger})"

    def __contains__(self, recipient: str) -> bool:
        if recipient in self.recipients:
            return True
        return False

    def _reset_game(self):
        self.STARTED = False
        self.WISHLIST = {}

    def handle_message(self, msg_body: str, sender: str) -> None:
        """
        Entrypoint method to start processing messages.

        1. Check is the sender is in our recipient list.

        2. Check the message body
            - If its the started trigger, handle accordingly
              based on if the game is started or not.
            - If the game has started, process the message
              as a wishlist.
            - Don't do anything if a valid sender sends a
              message when the game is not started.
        """

        if sender not in self:
            logger.warn(f"Unidentified number {sender}! 🤨📱")
            return

        if msg_body == self.start_trigger:
            return self.handle_start_trigger(sender)

        if self.STARTED:
            return self.handle_wishlist(msg_body, sender)

    def handle_start_trigger(self, sender: str) -> None:
        """
        Handle when a message is the game's start trigger string.

        If the game has already started, then warn the sender.
        If not started, updated self.STARTED, and prompt everyone for their wishlist!
        """

        if self.STARTED:
            return self.send_already_started_warning(sender)

        self.STARTED = True
        return self.send_wishlist_prompt()

    def handle_wishlist(self, msg_body: str, sender: str) -> None:
        """
        Handle when the message *should* be someone's wishlist.

        Store the message as the sender's wishlist, and wait until
        everyone has entered a wishlist to do the Secret Santa matching.
        Reset game after secret santa messages are sent.

        Note: The current implementation allows for someone to resend their
        wishlist unless they are the last sender.
        """

        self.WISHLIST[sender] = msg_body
        logger.debug(f"Entered wishlist: {list(self.WISHLIST.keys())} 🎁✅")

        if len(self.WISHLIST) < len(self.recipients):
            return self.send_pending(sender)

        self.send_pending(sender, last_sender=True)
        self.match_and_announce()
        self._reset_game()

    def send_wishlist_prompt(self) -> None:
        """
        Send all recipients the first message asking for their wishlist.
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            message = "Hello {}!\n\nPlease reply with your Secret Santa wishlist! 🎄🎁"

            # Schedule messages for all recipients
            outgoing_msgs = [
                executor.submit(
                    utils.send_message, message_body=message.format(name), recipient_number=number
                )
                for number, name in self.recipients.items()
            ]

            for future in concurrent.futures.as_completed(outgoing_msgs):
                _ = future.result()

    def send_already_started_warning(self, recipient: str) -> None:
        """
        Send recipient a message that the game has already started.
        """

        message = "Oops! Someone has already started the Secret Santa game! 😬"
        utils.send_message(message_body=message, recipient_number=recipient)

    def send_pending(self, recipient: str, last_sender=False) -> None:
        """
        Inform recipient that we're either waiting on more entries,
        or they were the last sender and we'll start matching!
        """

        name = self.recipients.get(recipient)

        message = f"Thank you, {name}!\n\n"
        if last_sender:
            message += "You were the last entry! 👏 Sit tight, we're calculating the matches!"
        else:
            message += "Sit tight! We're waiting on other entries... 👀🤫"

        utils.send_message(message_body=message, recipient_number=recipient)

    def match_and_announce(self) -> None:
        """
        Match Secret Santas and message to each recipient.
        """

        # ex. {'+1234567891': '+9876543219', ...}
        matches = matcher.match(list(self.recipients.keys()))

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            message = (
                "Your Secret Santa is...\n\n"
                "✨🎅🏼 {name} 🎅🏼✨\n\n"
                "Their wishlist is:\n{wishlist}\n\n"
                f"🚨 Remember! 🚨\n\nThe budget is ${settings.DOLLAR_BUDGET:.2f}!"
            )

            # Schedule messages for all recipients
            outgoing_msgs = [
                executor.submit(
                    utils.send_message,
                    message_body=message.format(
                        name=self.recipients.get(secret_santa_number).upper(),
                        wishlist=self.WISHLIST.get(secret_santa_number),
                    ),
                    recipient_number=recipient_number,
                )
                for recipient_number, secret_santa_number in matches.items()
            ]

            for future in concurrent.futures.as_completed(outgoing_msgs):
                _ = future.result()
