from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.db import get_config, set_config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_owner
def config_set(update, _context):
    _, key, value = update.message.text.split(' ')
    set_config(key, value)
    shown_value = value[:10]
    logger.info(f"Stored '{shown_value}' (cropped to 10 chars) with key '{key}'.")
    update.message.reply_text('ok')
    raise DispatcherHandlerStop()


@only_owner
def config_get(update, _context):
    _, key = update.message.text.split(' ')
    result = get_config(key)
    if result is None:
        logger.info(f"Replying with 'no value' message for key '{key}'.")
        update.message.reply_text(f"No value for key '{key}'.")
    else:
        shown_value = result[:10]
        logger.info(
            f"Replying with '{shown_value}' (cropped to 10 chars) for key '{key}'."
        )
        update.message.reply_text(result)
    raise DispatcherHandlerStop()
