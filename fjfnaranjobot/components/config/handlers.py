from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.config import config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# cmd --> GET_SET_OR_DEL --> GET_VAR --> end
#                        --> SET_VAR --> SET_VALUE --> end
#                        --> DEL_VAR --> end
#
# GET_SET_OR_DEL, GET_VAR, SET_VAR, DEL_VAR, SET_VALUE --> end
#

GET_SET_OR_DEL, GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(5)


@only_owner
def config_handler(update, _context):
    logger.info("Entering config conversation.")
    update.message.reply_text(
        "If you want to get the value for a configuration key, use /config_get . "
        "If you want to set the value, /config_set . "
        "If you want to clear it, /config_del . "
        "If you want to do something else, /config_cancel ."
    )
    return GET_SET_OR_DEL


def get_handler(update, _context):
    logger.info("Requesting key name to get its value.")
    update.message.reply_text("Tell me what key do you want to get.")
    return GET_VAR


def get_var_handler(update, _context):
    key = update.message.text
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
    return ConversationHandler.END


def set_handler(update, _context):
    logger.info("Requesting key name to set its value.")
    update.message.reply_text("Tell me what key do you want to set.")
    return SET_VAR


def set_var_handler(update, context):
    key = update.message.text
    context.user_data['key'] = key
    logger.info("Requesting key name to set its value.")
    update.message.reply_text(
        f"Tell me what value do you want to put in the key '{key}'."
    )
    return SET_VALUE


def set_value_handler(update, context):
    value = update.message.text
    key = context.user_data['key']
    del context.user_data['key']
    config[key] = value
    shown_value = value[:10]
    logger.info(f"Stored '{shown_value}' (cropped to 10 chars) with key '{key}'.")
    update.message.reply_text("I'll remember that.")
    return ConversationHandler.END


def del_handler(update, _context):
    logger.info("Requesting key name to clear its value.")
    update.message.reply_text("Tell me what key do you want to clear.")
    return DEL_VAR


def del_var_handler(update, _context):
    key = update.message.text
    try:
        del config[key]
    except KeyError:
        logger.info(f"Tried to delete config with key '{key}' but it didn't exists.")
        update.message.reply_text(f"I don't know anything about '{key}'.")
    else:
        logger.info(f"Deleting config with key '{key}'.")
        update.message.reply_text("I'll forget that.")
    return ConversationHandler.END


def cancel_handler(update, context):
    if 'key' in context.user_data:
        del context.user_data['key']
    logger.info("Abort config conversation.")
    update.message.reply_text("Ok.")
    return ConversationHandler.END


handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('config', config_handler)],
        states={
            GET_SET_OR_DEL: [
                CommandHandler('config_get', get_handler),
                CommandHandler('config_set', set_handler),
                CommandHandler('config_del', del_handler),
            ],
            GET_VAR: [MessageHandler(Filters.text, get_var_handler)],
            SET_VAR: [MessageHandler(Filters.text, set_var_handler)],
            SET_VALUE: [MessageHandler(Filters.text, set_value_handler)],
            DEL_VAR: [MessageHandler(Filters.text, del_var_handler)],
        },
        fallbacks=[CommandHandler('config_cancel', cancel_handler)],
    ),
)
