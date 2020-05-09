from contextlib import contextmanager
from os import environ, makedirs, remove
from os.path import isdir, isfile, join, split
from re import compile
from sqlite3 import connect

from fjfnaranjobot.logging import getLogger
from fjfnaranjobot.utils import EnvValueError, get_bot_data_dir

_BOT_DB_DEFAULT_NAME = 'bot.db'

logger = getLogger(__name__)

_state = {'initialized': False}


class InvalidKeyError(Exception):
    pass


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
            raise EnvValueError('Invalid dir name in BOT_DB_NAME var.')
    if not isfile(db_path):
        logger.debug("Initializing configuration database.")
        try:
            with open(db_path, 'wb'):
                pass
        except OSError:
            raise EnvValueError('Invalid file name in BOT_DB_NAME var.')
        with _cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')
    _state['initialized'] = True


def reset_state():
    _state['initialized'] = False
    if isfile(get_db_path()):
        remove(get_db_path())
    _ensure_db()


@contextmanager
def _cursor():
    conn = connect(get_db_path())
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


def _validate_key(key):
    validator = compile(r'^([a-zA-Z]+\.)*([a-zA-Z]+)+$')
    if validator.fullmatch(key) is None:
        raise InvalidKeyError(f"No valid value for key {key}.")


def set_key(key, value):
    _ensure_db()
    _validate_key(key)
    shown_value = value[:10]
    logger.debug(
        f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
    )
    with _cursor() as cur:
        cur.execute('SELECT value FROM config WHERE key=?', (key,))
        exists = cur.fetchone()
        if exists is None:
            cur.execute(
                'INSERT INTO config VALUES (?, ?) ', (key, value),
            )
        else:
            cur.execute(
                'UPDATE config SET key=?, value=? WHERE key=?', (key, value, key),
            )


def get_key(key):
    _ensure_db()
    _validate_key(key)
    logger.debug(f"Getting configuration value for key '{key}'.")
    with _cursor() as cur:
        cur.execute('SELECT value FROM config WHERE key=?', (key,))
        result = cur.fetchone()
    return None if result is None else result[0]
