from unittest.mock import MagicMock

from telegram.ext import DispatcherHandlerStop
from pytest import raises

from fjfnaranjobot.components.sorry.use_cases import sorry
from tests.base import BotTestCase


class SorryUseCasesTests(BotTestCase):
    def test_sorry_handler_processor(self):
        update = MagicMock()
        with raises(DispatcherHandlerStop):
            sorry(update, None)
        update.message.reply_text.assert_called_once()
        assert 'Sorry' in update.message.reply_text.call_args[0][0]
