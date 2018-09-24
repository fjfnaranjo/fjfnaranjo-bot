from logging import getLogger

from telegram.ext import MessageHandler, Filters


logger = getLogger(__name__)


def echo_handler_processor(bot, update):
    text = update.message.text
    logger.info(f'Echoing "{text}" back.')
    bot.send_message(chat_id=update.message.chat_id, text=text)


echo_handler = MessageHandler(Filters.text, echo_handler_processor)
