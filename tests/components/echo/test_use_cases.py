from unittest import TestCase
from unittest.mock import MagicMock

from telegram.ext import DispatcherHandlerStop
from pytest import raises

from fjfnaranjobot.components.echo.use_cases import echo


class EchoTests(TestCase):
    def test_echo_handler_processor(self):
        update = MagicMock()
        update.message.text = 'msg'
        with raises(DispatcherHandlerStop):
            echo(update, None)
        update.message.reply_text.assert_called_once_with('msg')
