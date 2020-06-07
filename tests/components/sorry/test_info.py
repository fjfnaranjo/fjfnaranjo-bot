from unittest.mock import sentinel

from fjfnaranjobot.components.sorry.info import logger, sorry_handler

from ...base import BotHandlerTestCase


class SorryHandlersTests(BotHandlerTestCase):
    def test_sorry_handler_processor(self):
        with self.assert_log_dispatch('Sending \'sorry\' back to the user.', logger):
            sorry_handler(*self.update_and_context)
        self.assert_message_chat_text(
            sentinel.chat_id, 'I don\'t know what to do about that. Sorry :('
        )
