from fjfnaranjobot.components.sorry.handlers import logger, sorry_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.sorry.handlers'


class SorryHandlersTests(BotHandlerTestCase):
    def test_sorry_handler_processor(self):
        with self.assert_log_dispatch('Sending \'sorry\' back to the user.', logger):
            sorry_handler(*self.update_and_context)
        self.assert_reply('I don\'t know what to do about that. Sorry :(')
