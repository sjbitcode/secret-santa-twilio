import unittest

from secret_santa import matcher


class MatcherTests(unittest.TestCase):
    RECIPIENTS = {
        "+1111111111": "Alice",
        "+2222222222": "Bob",
    }

    def test_matcher(self):
        match_dict = matcher.match(list(self.RECIPIENTS.keys()))

        self.assertEqual(len(match_dict), len(self.RECIPIENTS))
        for key, val in match_dict.items():
            self.assertNotEqual(key, val)
