from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.config import config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def config_set(update, _context):
    _, key, value = update.message.text.split(' ')
    config[key] = value
    shown_value = value[:10]
    logger.info(f"Stored '{shown_value}' (cropped to 10 chars) with key '{key}'.")
    update.message.reply_text("I'll remember that.")
    raise DispatcherHandlerStop()


def config_get(update, _context):
    _, key = update.message.text.split(' ')
    try:
        result = config[key]
    except KeyError:
        logger.info(f"Replying with 'no value' message for key '{key}'.")
        update.message.reply_text(f"No value for key '{key}'.")
    else:
        shown_value = result[:10]
        logger.info(
            f"Replying with '{shown_value}' (cropped to 10 chars) for key '{key}'."
        )
        update.message.reply_text(result)
    raise DispatcherHandlerStop()


def config_del(update, _context):
    _, key = update.message.text.split(' ')
    try:
        del config[key]
    except KeyError:
        logger.info(f"Tried to delete config with key '{key}' but it didn't exists.")
        update.message.reply_text(f"I don't know anything about '{key}'.")
    else:
        logger.info(f"Deleting config with key '{key}'.")
        update.message.reply_text("I'll forget that.")
    raise DispatcherHandlerStop()
