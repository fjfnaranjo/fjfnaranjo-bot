from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import Command
from fjfnaranjobot.config import config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# config_handler states
#
# cmd --> GET_SET_OR_DEL --> GET_VAR --> end
#                        --> SET_VAR --> SET_VALUE --> end
#                        --> DEL_VAR --> end
#
# * --> end
#

GET_SET_OR_DEL, GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(5)


@only_owner
def config_handler(update, context):
    logger.info("Entering config conversation.")
    reply = update.message.reply_text(
        "If you want to get the value for a configuration key, use /config_get . "
        "If you want to set the value, /config_set . "
        "If you want to clear it, /config_del . "
        "If you want to do something else, /config_cancel ."
    )
    context.user_data['message_ids'] = (reply.chat.id, reply.message_id)
    return GET_SET_OR_DEL


def get_handler(_update, context):
    logger.info("Requesting key name to get its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to get. "
        "If you want to do something else, /config_cancel .",
        *context.user_data['message_ids'],
    )
    return GET_VAR


def get_var_handler(update, context):
    key = update.message.text
    try:
        result = config[key]
    except ValueError:
        logger.info(f"Can't get invalid config key '{key}'.")
        context.bot.edit_message_text(
            f"The key '{key}' is not a valid key. "
            "Tell me another key you want to get. "
            "If you want to do something else, /config_cancel .",
            *context.user_data['message_ids'],
        )
        return GET_VAR
    except KeyError:
        logger.info(f"Replying with 'no value' message for key '{key}'.")
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text(f"No value for key '{key}'.")
    else:
        shown_value = result[:10]
        logger.info(
            f"Replying with '{shown_value}' (cropped to 10 chars) for key '{key}'."
        )
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text(f"The value for key '{key}' is '{result}'.")
    return ConversationHandler.END


def set_handler(_update, context):
    logger.info("Requesting key name to set its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to set. "
        "If you want to do something else, /config_cancel .",
        *context.user_data['message_ids'],
    )
    return SET_VAR


def set_var_handler(update, context):
    key = update.message.text
    try:
        config[key]
    except ValueError:
        logger.info(f"Can't set invalid config key '{key}'.")
        context.bot.edit_message_text(
            f"The key '{key}' is not a valid key. "
            "Tell me another key you want to set. "
            "If you want to do something else, /config_cancel .",
            *context.user_data['message_ids'],
        )
        return SET_VAR
    except KeyError:
        pass
    context.user_data['key'] = key
    logger.info("Requesting value to set the key.")
    context.bot.edit_message_text(
        f"Tell me what value do you want to put in the key '{key}'. "
        "If you want to do something else, /config_cancel .",
        *context.user_data['message_ids'],
    )
    return SET_VALUE


def set_value_handler(update, context):
    value = update.message.text
    key = context.user_data['key']
    del context.user_data['key']
    config[key] = value
    shown_value = value[:10]
    logger.info(f"Stored '{shown_value}' (cropped to 10 chars) in key '{key}'.")
    context.bot.delete_message(*context.user_data['message_ids'])
    del context.user_data['message_ids']
    update.message.reply_text("I'll remember that.")
    return ConversationHandler.END


def del_handler(_update, context):
    logger.info("Requesting key name to clear its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to clear. "
        "If you want to do something else, /config_cancel .",
        *context.user_data['message_ids'],
    )
    return DEL_VAR


def del_var_handler(update, context):
    key = update.message.text
    try:
        del config[key]
    except ValueError:
        logger.info(f"Can't delete invalid config key '{key}'.")
        context.bot.edit_message_text(
            f"The key '{key}' is not a valid key. "
            "Tell me another key you want to clear. "
            "If you want to do something else, /config_cancel .",
            *context.user_data['message_ids'],
        )
        return DEL_VAR
    except KeyError:
        logger.info(f"Tried to delete config with key '{key}' but it didn't exists.")
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text(f"I don't know anything about '{key}'.")
    else:
        logger.info(f"Deleting config with key '{key}'.")
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text("I'll forget that.")
    return ConversationHandler.END


def cancel_handler(update, context):
    if 'key' in context.user_data:
        del context.user_data['key']
    if 'message_ids' in context.user_data:
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
    logger.info("Abort config conversation.")
    update.message.reply_text("Ok.")
    return ConversationHandler.END


handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('config', config_handler)],
        states={
            GET_SET_OR_DEL: [
                CommandHandler('config_cancel', cancel_handler),
                CommandHandler('config_get', get_handler),
                CommandHandler('config_set', set_handler),
                CommandHandler('config_del', del_handler),
            ],
            GET_VAR: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.text, get_var_handler),
            ],
            SET_VAR: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.text, set_var_handler),
            ],
            SET_VALUE: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.text, set_value_handler),
            ],
            DEL_VAR: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.text, del_var_handler),
            ],
        },
        fallbacks=[CommandHandler('config_cancel', cancel_handler)],
    ),
)

commands = (Command("Edit bot configuration.", None, 'config',),)
