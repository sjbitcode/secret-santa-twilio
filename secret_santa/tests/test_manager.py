import unittest
from unittest.mock import call, patch

from secret_santa import manager, settings

ALICE_NUMBER = "+1234567891"
BOB_NUMBER = "+9876543219"
UNREGISTERED_SENDER = "+1111111111"
RECIPIENTS = {ALICE_NUMBER: "Alice", BOB_NUMBER: "Bob"}


class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.game = manager.Game(RECIPIENTS, settings.START_TRIGGER)
        self.mock_logger = patch("secret_santa.manager.logger").start()
        self.mock_send_message = patch("secret_santa.utils.send_message", autospec=True).start()
        self.addCleanup(patch.stopall)

    def test_game_repr(self):
        self.assertEqual(repr(self.game), f"Game({RECIPIENTS}, {settings.START_TRIGGER})")

    @patch.object(manager.Game, "handle_start_trigger", autospec=True)
    @patch.object(manager.Game, "handle_wishlist", autospec=True)
    def test_handle_message_for_unknown_number(
        self, mock_game_handle_wishlist, mock_game_start_trigger
    ):
        self.game.handle_message("Howdy!", UNREGISTERED_SENDER)

        self.mock_logger.warn.assert_called_once_with(
            f"Unidentified number {UNREGISTERED_SENDER}! 🤨📱"
        )
        mock_game_handle_wishlist.assert_not_called()
        mock_game_start_trigger.assert_not_called()

    @patch.object(manager.Game, "handle_start_trigger", autospec=True)
    @patch.object(manager.Game, "handle_wishlist", autospec=True)
    def test_handle_message_when_message_is_start_trigger(
        self, mock_game_handle_wishlist, mock_game_start_trigger
    ):
        self.game.handle_message(settings.START_TRIGGER, ALICE_NUMBER)

        mock_game_start_trigger.assert_called_once_with(self.game, ALICE_NUMBER)
        mock_game_handle_wishlist.assert_not_called()

    @patch.object(manager.Game, "handle_start_trigger", autospec=True)
    @patch.object(manager.Game, "handle_wishlist", autospec=True)
    def test_handle_message_when_message_is_not_start_trigger_and_started_false(
        self, mock_game_handle_wishlist, mock_game_start_trigger
    ):
        self.game.STARTED = False

        self.game.handle_message("cookies", ALICE_NUMBER)

        mock_game_handle_wishlist.assert_not_called()
        mock_game_start_trigger.assert_not_called()

    @patch.object(manager.Game, "handle_start_trigger", autospec=True)
    @patch.object(manager.Game, "handle_wishlist", autospec=True)
    def test_handle_message_when_message_is_not_start_trigger_and_started_true(
        self, mock_game_handle_wishlist, mock_game_start_trigger
    ):
        self.game.STARTED = True

        self.game.handle_message("cookies", ALICE_NUMBER)

        mock_game_handle_wishlist.assert_called_once_with(self.game, "cookies", ALICE_NUMBER)
        mock_game_start_trigger.assert_not_called()

    @patch.object(manager.Game, "send_already_started_warning", autospec=True)
    @patch.object(manager.Game, "send_wishlist_prompt", autospec=True)
    def test_handle_start_trigger_when_started_true(
        self, mock_send_wishlist_prompt, mock_send_warning
    ):
        self.game.STARTED = True

        self.game.handle_start_trigger(ALICE_NUMBER)

        mock_send_warning.assert_called_once_with(self.game, ALICE_NUMBER)
        mock_send_wishlist_prompt.assert_not_called()

    @patch.object(manager.Game, "send_already_started_warning", autospec=True)
    @patch.object(manager.Game, "send_wishlist_prompt", autospec=True)
    def test_handle_start_trigger_when_started_false(
        self, mock_send_wishlist_prompt, mock_send_warning
    ):
        self.game.STARTED = False

        self.game.handle_start_trigger(ALICE_NUMBER)

        mock_send_wishlist_prompt.assert_called_once()
        self.assertTrue(self.game.STARTED)
        mock_send_warning.assert_not_called()

    @patch.object(manager.Game, "send_pending", autospec=True)
    @patch.object(manager.Game, "match_and_announce", autospec=True)
    def test_handle_wishlist_incomplete(self, mock_match, mock_send_pending):
        self.game.WISHLIST = {}

        self.game.handle_wishlist("cookies", ALICE_NUMBER)

        self.assertEqual(self.game.WISHLIST, {ALICE_NUMBER: "cookies"})
        self.mock_logger.debug.assert_called_once_with(f"Entered wishlist: {[ALICE_NUMBER]} 🎁✅")
        mock_send_pending.assert_called_once_with(self.game, ALICE_NUMBER)
        mock_match.assert_not_called()

    @patch.object(manager.Game, "send_pending", autospec=True)
    @patch.object(manager.Game, "match_and_announce", autospec=True)
    def test_handle_wishlist_incomplete_duplicate_sender(self, mock_match, mock_send_pending):
        self.game.WISHLIST = {ALICE_NUMBER: "sweater"}

        self.game.handle_wishlist("cookies", ALICE_NUMBER)

        self.assertEqual(self.game.WISHLIST, {ALICE_NUMBER: "cookies"})
        self.mock_logger.debug.assert_called_once_with(f"Entered wishlist: {[ALICE_NUMBER]} 🎁✅")
        mock_send_pending.assert_called_once_with(self.game, ALICE_NUMBER)
        mock_match.assert_not_called()

    @patch.object(manager.Game, "send_pending", autospec=True)
    @patch.object(manager.Game, "match_and_announce", autospec=True)
    def test_handle_wishlist_complete(self, mock_match_and_announce, mock_send_pending):
        self.game.WISHLIST = {ALICE_NUMBER: "cookies"}

        self.game.handle_wishlist("coffee", BOB_NUMBER)

        mock_send_pending.assert_called_once_with(self.game, BOB_NUMBER, last_sender=True)
        mock_match_and_announce.assert_called_once()
        self.assertEqual(self.game.WISHLIST, {})
        self.assertFalse(self.game.STARTED)

    def test_send_wishlist_prompt(self):
        initial_prompt = "Please reply with your Secret Santa wishlist! 🎄🎁"
        expected = [
            call(message_body=f"Hello {val}!\n\n{initial_prompt}", recipient_number=key)
            for key, val in self.game.recipients.items()
        ]

        self.game.send_wishlist_prompt()

        self.assertEqual(self.mock_send_message.call_count, 2)
        self.assertEqual(self.mock_send_message.call_args_list, expected)

    def test_send_already_started_warning(self):
        expected = [
            call(
                message_body="Oops! Someone has already started the Secret Santa game! 😬",
                recipient_number=BOB_NUMBER,
            )
        ]

        self.game.send_already_started_warning(BOB_NUMBER)

        self.assertEqual(self.mock_send_message.call_args_list, expected)

    def test_send_pending(self):
        expected = [
            call(
                message_body=(
                    f"Thank you, {RECIPIENTS.get(BOB_NUMBER)}!\n\n"
                    "Sit tight! We're waiting on other entries... 👀🤫"
                ),
                recipient_number=BOB_NUMBER,
            )
        ]

        self.game.send_pending(BOB_NUMBER)

        self.assertEqual(self.mock_send_message.call_args_list, expected)

    def test_send_pending_to_last_sender(self):
        expected = [
            call(
                message_body=(
                    f"Thank you, {RECIPIENTS.get(BOB_NUMBER)}!\n\n"
                    "You were the last entry! 👏 Sit tight, we're calculating the matches!"
                ),
                recipient_number=BOB_NUMBER,
            )
        ]

        self.game.send_pending(BOB_NUMBER, last_sender=True)

        self.assertEqual(self.mock_send_message.call_args_list, expected)

    @patch("secret_santa.matcher.match", autospec=True)
    def test_match_and_announce(self, mock_match):
        mock_match.return_value = {ALICE_NUMBER: BOB_NUMBER, BOB_NUMBER: ALICE_NUMBER}
        self.game.WISHLIST = {
            ALICE_NUMBER: "books 📚\nhiking boots 🥾\ngift card 🛍",
            BOB_NUMBER: "chocolate 🍫\ncoffee ☕️\nsocks 🧦",
        }
        expected = [
            call(
                message_body=(
                    f"Your Secret Santa is...\n\n"
                    f"✨🎅🏼 {RECIPIENTS.get(val).upper()} 🎅🏼✨\n\n"
                    f"Their wishlist is:\n{self.game.WISHLIST.get(val)}\n\n"
                    f"🚨 Remember! 🚨\n\nThe budget is ${settings.DOLLAR_BUDGET:.2f}!"
                ),
                recipient_number=key,
            )
            for key, val in mock_match(list(RECIPIENTS.keys())).items()
        ]

        self.game.match_and_announce()

        self.assertEqual(self.mock_send_message.call_args_list, expected)
