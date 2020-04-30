from unittest.mock import patch

from fjfnaranjobot.component.echo import echo_handler_processor


@patch('telegram.bot.Bot')
@patch('telegram.update.Update')
def test_echo_handler_processor(bot, update):
    result = echo_handler_processor(bot, update)
    assert result == None
    assert bot.send_message.called
