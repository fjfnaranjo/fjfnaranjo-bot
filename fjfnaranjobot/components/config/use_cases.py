from fjfnaranjobot.config import set_key, get_key
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def config_set(update, _context):
    _, key, value = update.message.text.split(' ')
    set_key(key, value)
    shown_value = value[:10]
    logger.info(f"Stored '{shown_value}' (cropped to 10 chars) with key '{key}'.")
    update.message.reply_text('ok')


def config_get(update, _context):
    _, key = update.message.text.split(' ')
    result = get_key(key)
    if result is None:
        logger.info(f"Replying with 'no value' message for key '{key}'.")
        update.message.reply_text(f"No value for key '{key}'.")
    else:
        shown_value = result[:10]
        logger.info(
            f"Replying with '{shown_value}' (cropped to 10 chars) for key '{key}'."
        )
        update.message.reply_text(result)
