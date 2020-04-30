from logging import getLogger


logger = getLogger(__name__)


def echo(bot, update):
    text = update.message.text
    logger.info(f"Echoing '{text}' back.")
    bot.send_message(chat_id=update.message.chat_id, text=text)
