from unittest.mock import patch, sentinel


from fjfnaranjobot.components.echo.use_cases import echo


@patch('telegram.bot.Bot')
@patch('telegram.update.Update')
def test_echo_handler_processor(bot, update):
    update.message.text = sentinel.text
    update.message.chat_id = sentinel.chat_id
    echo(bot, update)
    bot.send_message.assert_called_with(chat_id=sentinel.chat_id, text=sentinel.text)
