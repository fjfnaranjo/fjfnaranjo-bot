from fjfnaranjobot.components.sorry.handlers import logger, sorry_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.sorry.handlers'


class SorryHandlersTests(BotHandlerTestCase):
    def test_sorry_handler_processor(self):
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                sorry_handler(self._update, None)
        self._update.message.reply_text.assert_called_once()
        assert (
            'I don\'t know what to do about that. Sorry :('
            in self._update.message.reply_text.call_args[0][0]
        )
        assert 'Sending \'sorry\' back to the user.' in logs.output[0]
