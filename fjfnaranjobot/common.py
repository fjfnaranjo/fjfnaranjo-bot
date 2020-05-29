from os import environ

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    StringCommandHandler,
)

_BOT_DATA_DIR_DEFAULT = 'botdata'


def get_bot_data_dir():
    return environ.get('BOT_DATA_DIR', _BOT_DATA_DIR_DEFAULT)


def _get_handler_callback_name(handler):
    callback_function = getattr(handler, 'callback', None)
    return (
        callback_function.__name__
        if callback_function is not None and callable(callback_function)
        else '<unknown callback>'
    )


def get_names_callbacks(handler):
    names_callbacks = []

    if isinstance(handler, ConversationHandler):
        for entry_point in handler.entry_points:
            return get_names_callbacks(entry_point)
    else:
        callback_name = _get_handler_callback_name(handler)
        if isinstance(handler, CommandHandler):
            for command in handler.command:
                names_callbacks.append((command, callback_name,))
        elif isinstance(handler, StringCommandHandler):
            names_callbacks.append((handler.command, callback_name,))
        elif isinstance(handler, MessageHandler):
            names_callbacks.append(('<message>', callback_name,))
        else:
            names_callbacks.append(('<unknown command>', callback_name,))

    return names_callbacks
