import mock

from fjfnaranjobot.component.echo import echo_handler_processor


@mock.patch('telegram.bot.Bot')
@mock.patch('telegram.update.Update')
def test_echo_handler_processor(bot, update):
    result = echo_handler_processor(bot, update)
    assert result == None
    assert bot.send_message.called
