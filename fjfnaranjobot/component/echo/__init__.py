from telegram.ext import MessageHandler, Filters


def echo_handler_processor(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


echo_handler = MessageHandler(Filters.text, echo_handler_processor)
