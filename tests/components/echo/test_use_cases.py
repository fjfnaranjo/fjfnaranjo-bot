from unittest.mock import patch, sentinel


from fjfnaranjobot.components.echo.use_cases import echo


@patch('telegram.update.Update')
@patch('telegram.bot.Bot')
def test_echo_handler_processor(bot, update):
    update.message.text = 'msg'
    update.message.chat_id = sentinel.chat_id
    echo(bot, update)
    bot.send_message.assert_called_once_with(chat_id=sentinel.chat_id, text='msg')
