from fjfnaranjobot.components.sorry.use_cases import sorry
from tests.base import BotUseCaseTestCase


class SorryUseCasesTests(BotUseCaseTestCase):
    def test_sorry_handler_processor(self):
        with self._raises_dispatcher_stop():
            sorry(self.update, None)
        self.update.message.reply_text.assert_called_once()
        assert 'Sorry' in self.update.message.reply_text.call_args[0][0]
