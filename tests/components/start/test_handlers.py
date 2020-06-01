from fjfnaranjobot.components.start.handlers import logger, start_handler

from ...base import BotHandlerTestCase


class SorryHandlersTests(BotHandlerTestCase):
    def test_start_handler_processor(self):
        with self.assert_log_dispatch('Greeting a new user with id 99.', logger):
            start_handler(*self.update_and_context)
        self.assert_reply('Welcome. I\'m fjfnaranjo\'s bot. How can I help you?')
