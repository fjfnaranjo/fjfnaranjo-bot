from os import environ

_BOT_DATA_DIR_DEFAULT = 'botdata'
_BOT_OWNER_NAME_DEFAULT = 'fjfnaranjo'
_BOT_COMPONENTS_DEFAULT = "start,config,friends,commands,terraria,sorry"

SORRY_TEXT = "I don't know what to do about that. Sorry :("


def get_bot_data_dir():
    return environ.get('BOT_DATA_DIR', _BOT_DATA_DIR_DEFAULT)


def get_bot_owner_name():
    return environ.get('BOT_OWNER_NAME', _BOT_OWNER_NAME_DEFAULT)


def get_bot_components():
    return environ.get('BOT_COMPONENTS', _BOT_COMPONENTS_DEFAULT)


class User:
    def __init__(self, id_, username):
        self.id = int(id_)
        self.username = username


command_list = []
command_list_dev = []
