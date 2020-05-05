from telegram.ext.dispatcher import DispatcherHandlerStop

from fjfnaranjobot.logging import getLogger


logger = getLogger(__name__)


def echo(update, _context):
    text = update.message.text
    shown_text = text[:10]
    logger.info(f"Echoing '{shown_text}' (cropped to 10 chars) back.")
    update.message.reply_text(text)
    raise DispatcherHandlerStop()
