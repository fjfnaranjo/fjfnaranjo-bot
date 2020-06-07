from telegram.ext import DispatcherHandlerStop, Filters, MessageHandler

from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def sorry_handler(update, context):
    logger.info("Sending 'sorry' back to the user.")

    context.bot.send_message(
        update.message.chat.id, SORRY_TEXT,
    )
    raise DispatcherHandlerStop()


handlers = (MessageHandler(Filters.text, sorry_handler),)
