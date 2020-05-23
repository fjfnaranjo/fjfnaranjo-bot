from contextlib import contextmanager
from os import environ, makedirs, remove
from os.path import isdir, isfile, join, split
from sqlite3 import connect

from fjfnaranjobot.common import EnvValueError, get_bot_data_dir
from fjfnaranjobot.logging import getLogger

_BOT_DB_DEFAULT_NAME = 'bot.db'

logger = getLogger(__name__)

_state = {'initialized': False}


def get_db_path():
    return join(get_bot_data_dir(), environ.get('BOT_DB_NAME', _BOT_DB_DEFAULT_NAME))


def _ensure_db():
    if _state['initialized']:
        return
    db_path = get_db_path()
    db_dir, _ = split(db_path)
    if not isdir(db_dir):
        try:
            makedirs(db_dir)
        except:
            raise EnvValueError("Invalid dir name in BOT_DB_NAME var.")
    if not isfile(db_path):
        logger.debug("Initializing configuration database.")
        try:
            with open(db_path, 'wb'):
                pass
        except OSError:
            raise EnvValueError("Invalid file name in BOT_DB_NAME var.")
    _state['initialized'] = True


def reset(create=True):
    _state['initialized'] = False
    if isfile(get_db_path()):
        remove(get_db_path())
    if create:
        _ensure_db()


@contextmanager
def cursor():
    _ensure_db()
    conn = connect(get_db_path())
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()
