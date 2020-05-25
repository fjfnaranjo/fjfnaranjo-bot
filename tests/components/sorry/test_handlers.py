from fjfnaranjobot.components.sorry.handlers import logger, sorry_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.sorry.handlers'


class SorryHandlersTests(BotHandlerTestCase):
    def test_sorry_handler_processor(self):
        with self._assert_reply_log_dispatch(
            'I don\'t know what to do about that. Sorry :(',
            'Sending \'sorry\' back to the user.',
            logger,
        ):
            sorry_handler(self._update, None)
