from os import environ

_BOT_DATA_DIR_DEFAULT = 'botdata'

SORRY_TEXT = "I don't know what to do about that. Sorry :("


def get_bot_data_dir():
    return environ.get('BOT_DATA_DIR', _BOT_DATA_DIR_DEFAULT)


class User:
    def __init__(self, id_, username):
        self.id = int(id_)
        self.username = username
