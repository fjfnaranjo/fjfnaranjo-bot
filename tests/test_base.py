from .base import BotHandlerTestCase


class BaseTests(BotHandlerTestCase):
    def test_no_command_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.user_is_unknown(True)

    def test_empty_command_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.user_is_unknown(None, True)
