from os import environ

_BOT_DATA_DIR_DEFAULT = 'botdata'


def get_bot_data_dir():
    return environ.get('BOT_DATA_DIR', _BOT_DATA_DIR_DEFAULT)


class EnvValueError(Exception):
    pass
