from unittest.mock import MagicMock


from fjfnaranjobot.components.echo.use_cases import echo


def test_echo_handler_processor():
    update = MagicMock()
    update.message.text = 'msg'
    echo(update, None)
    update.message.reply_text.assert_called_once_with('msg')
