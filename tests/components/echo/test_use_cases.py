from unittest.mock import patch

from fjfnaranjobot.components.echo.use_cases import echo


@patch('telegram.bot.Bot')
@patch('telegram.update.Update')
def test_echo_handler_processor(bot, update):
    result = echo(bot, update)
    assert result is None
    assert bot.send_message.called
