from fjfnaranjobot.components.sorry.use_cases import logger, sorry

from ...base import BotUseCaseTestCase


class SorryUseCasesTests(BotUseCaseTestCase):
    def test_sorry_handler_processor(self):
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                sorry(self._update, None)
        self._update.message.reply_text.assert_called_once()
        assert (
            'I don\'t know what to do about that. Sorry :('
            in self._update.message.reply_text.call_args[0][0]
        )
        assert 'Sending \'sorry\' back to the user.' in logs.output[0]
