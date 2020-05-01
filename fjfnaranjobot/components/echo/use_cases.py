from fjfnaranjobot.logging import getLogger


logger = getLogger(__name__)


def echo(bot, update):
    text = update.message.text
    shown_text = text[:10]
    logger.info(f"Echoing '{shown_text}' (cropped to 10 chars) back.")
    bot.send_message(chat_id=update.message.chat_id, text=text)
