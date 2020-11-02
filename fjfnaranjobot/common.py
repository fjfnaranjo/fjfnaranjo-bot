from os import environ

_BOT_OWNER_NAME_DEFAULT = 'fjfnaranjo'
_BOT_COMPONENTS_DEFAULT = "start,config,friends,commands,terraria,sorry"

SORRY_TEXT = "I don't know what to do about that. Sorry :("

LOG_VALUE_MAX_LENGHT = 16


command_list = []


def get_bot_owner_name():
    return environ.get('BOT_OWNER_NAME', _BOT_OWNER_NAME_DEFAULT)


def get_bot_components():
    return environ.get('BOT_COMPONENTS', _BOT_COMPONENTS_DEFAULT)


class User:
    def __init__(self, id_, username):
        self.id = int(id_)
        self.username = username


class Command:
    def __init__(self, description, prod_command, dev_command):
        self.description = description
        self.prod_command = prod_command
        self.dev_command = dev_command


class ScheduleEntry:
    def __init__(self, name, schedule, signature, **kwargs):
        self.name = name
        self.schedule = schedule
        self.signature = signature
        self.extra_args = kwargs


def inline_handler(inlines, logger):
    def inline_handler_function(update, context):
        logger.debug("Received inline selection.")
        query = update.callback_query.data
        logger.debug(f"Inline selection was '{query}'.")
        if query in inlines:
            return inlines[query](update, context)
        else:
            raise ValueError(f"No valid handlers for query '{query}'.")

    return inline_handler_function


def quote_value_for_log(value):
    if len(value) <= LOG_VALUE_MAX_LENGHT:
        return f"'{value}'"
    else:
        shown_value = value[:LOG_VALUE_MAX_LENGHT]
        return f"'{shown_value}' (cropped to {LOG_VALUE_MAX_LENGHT} chars)"
