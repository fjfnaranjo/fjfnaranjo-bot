# TODO: Review all tests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import Command, inline_handler, quote_value_for_log
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


def _clear_context_data(context):
    chat_data_known_keys = ['chat_id', 'message_id', 'key']
    for key in chat_data_known_keys:
        if key in context.chat_data:
            del context.chat_data[key]


_cancel_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
)


@only_owner
def config_handler(update, context):
    logger.info("Entering config conversation.")
    keyboard = [
        [
            InlineKeyboardButton("Get", callback_data='get'),
            InlineKeyboardButton("Set", callback_data='set'),
            InlineKeyboardButton("Delete", callback_data='del'),
        ],
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    reply = update.message.reply_text(
        "You can get the value for a configuration key, "
        "set it of change it if exists, or clear the key. "
        "You can also cancel the config command at any time.",
        reply_markup=reply_markup,
    )
    context.chat_data['chat_id'] = reply.chat.id
    context.chat_data['message_id'] = reply.message_id
    return GET_SET_OR_DEL


def get_handler(_update, context):
    logger.info("Requesting key name to get its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to get.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return GET_VAR


def get_var_handler(update, context):
    key = update.message.text
    shown_key = quote_value_for_log(key)
    logger.info(f"Received key name {shown_key}.")
    try:
        result = config[key]
    except (ValueError, KeyError) as e:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
        if isinstance(e, ValueError):
            logger.info("Key was invalid.")
            context.bot.send_message(
                context.chat_data['chat_id'], f"The key '{key}' is not a valid key.",
            )
        else:
            logger.info("Key doesn't exists.")
            context.bot.send_message(
                context.chat_data['chat_id'], f"The key '{key}' doesn't exists.",
            )
        _clear_context_data(context)
        return ConversationHandler.END
    else:
        shown_result = quote_value_for_log(result)
        logger.info(f"Replying with result {shown_result}.")
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
        context.bot.send_message(
            context.chat_data['chat_id'], f"The value for key '{key}' is '{result}'."
        )
        _clear_context_data(context)
        return ConversationHandler.END


def set_handler(_update, context):
    logger.info("Requesting key name to set its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to set.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return SET_VAR


def set_var_handler(update, context):
    key = update.message.text
    shown_key = quote_value_for_log(key)
    logger.info(f"Received key name {shown_key}.")
    try:
        config[key]
    except ValueError:
        logger.info("Can't set invalid config key 'invalid-key'.")
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], f"The key '{key}' is not a valid key."
        )
        _clear_context_data(context)
        return ConversationHandler.END
    except KeyError:
        pass
    context.chat_data['key'] = key
    logger.info("Requesting value to set the key.")
    context.bot.edit_message_text(
        f"Tell me what value do you want to put in the key '{key}'.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return SET_VALUE


def set_value_handler(update, context):
    value = update.message.text
    shown_value = quote_value_for_log(value)
    logger.info(f"Received value {shown_value}.")
    key = context.chat_data['key']
    del context.chat_data['key']
    config[key] = value
    logger.info(f"Stored {shown_value} in key '{key}'.")
    context.bot.delete_message(
        context.chat_data['chat_id'], context.chat_data['message_id'],
    )
    context.bot.send_message(context.chat_data['chat_id'], "I'll remember that.")
    _clear_context_data(context)
    return ConversationHandler.END


def del_handler(_update, context):
    logger.info("Requesting key name to clear its value.")
    context.bot.edit_message_text(
        "Tell me what key do you want to clear.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return DEL_VAR


def del_var_handler(update, context):
    key = update.message.text
    shown_key = quote_value_for_log(key)
    logger.info(f"Received key name {shown_key}.")
    try:
        del config[key]
    except (ValueError, KeyError) as e:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
        if isinstance(e, ValueError):
            logger.info("Key was invalid.")
            context.bot.send_message(
                context.chat_data['chat_id'], f"The key '{key}' is not a valid key.",
            )
        else:
            logger.info("Key doesn't exists.")
            context.bot.send_message(
                context.chat_data['chat_id'], f"The key '{key}' doesn't exists.",
            )
        _clear_context_data(context)
        return ConversationHandler.END
    else:
        logger.info(f"Deleting config with key '{key}'.")
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
        context.bot.send_message(context.chat_data['chat_id'], "I'll forget that.")
        _clear_context_data(context)
        return ConversationHandler.END


def cancel_handler(_update, context):
    logger.info("Abort config conversation.")
    if 'message_id' in context.chat_data:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
    context.bot.send_message(context.chat_data['chat_id'], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


cancel_inlines = {
    'cancel': cancel_handler,
}
action_inlines = {
    'get': get_handler,
    'set': set_handler,
    'del': del_handler,
    'cancel': cancel_handler,
}


handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('config', config_handler)],
        states={
            GET_SET_OR_DEL: [
                CallbackQueryHandler(inline_handler(action_inlines, logger)),
            ],
            GET_VAR: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.text, get_var_handler),
            ],
            SET_VAR: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.text, set_var_handler),
            ],
            SET_VALUE: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.text, set_value_handler),
            ],
            DEL_VAR: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.text, del_var_handler),
            ],
        },
        fallbacks=[],
    ),
)

commands = (Command("Edit bot configuration.", None, 'config',),)
