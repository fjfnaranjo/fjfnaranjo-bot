from telegram.ext import DispatcherHandlerStop, Filters, MessageHandler

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

group = 90


def sorry_handler(update, _context):
    logger.info("Sending 'sorry' back to the user.")
    update.message.reply_text("I don't know what to do about that. Sorry :(")
    raise DispatcherHandlerStop()


handlers = (MessageHandler(Filters.text, sorry_handler),)
