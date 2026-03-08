from os import environ

_BOT_OWNER_NAME_DEFAULT = "fjfnaranjo"
_BOT_COMPONENTS_DEFAULT = "start,config,friends,commands,sorry"

# TODO: This can be a class or another single import definition
SORRY_TEXT = "I don't know what to do about that. Sorry :("
NEXT_PAGE_CAPTION = "Next page"
RESTART_PAGINATOR_CAPTION = "Start again"
DEFAULT_PAGE_SIZE = 5
CANCEL_CAPTION = "Cancel"

LOG_VALUE_MAX_LENGHT = 16


command_list = []


def get_bot_owner_name():
    return environ.get("BOT_OWNER_NAME", _BOT_OWNER_NAME_DEFAULT)


def get_bot_components():
    return environ.get("BOT_COMPONENTS", _BOT_COMPONENTS_DEFAULT)


class User:
    def __init__(self, id_, username):
        self.id = int(id_)
        self.username = username


class ScheduleEntry:
    def __init__(self, name, schedule, signature, **kwargs):
        self.name = name
        self.schedule = schedule
        self.signature = signature
        self.extra_args = kwargs


def quote_value_for_log(value):
    if len(value) <= LOG_VALUE_MAX_LENGHT:
        return f"'{value}'"
    else:
        shown_value = value[:LOG_VALUE_MAX_LENGHT]
        return f"'{shown_value}' (cropped to {LOG_VALUE_MAX_LENGHT} chars)"
