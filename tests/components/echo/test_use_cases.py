from unittest import TestCase
from unittest.mock import MagicMock


from fjfnaranjobot.components.echo.use_cases import echo


class EchoTests(TestCase):
    def test_echo_handler_processor(self):
        update = MagicMock()
        update.message.text = 'msg'
        echo(update, None)
        update.message.reply_text.assert_called_once_with('msg')
