from contextlib import contextmanager
from os import environ
from os.path import join
from sqlite3 import connect

from fjfnaranjobot.logging import getLogger


BOT_DATA_DIR = environ.get('BOT_DATA_DIR', '')
BOT_DB = environ.get('BOT_DB', 'bot.db')

logger = getLogger(__name__)

state = {'initialized': False}


@contextmanager
def _cursor():
    conn = connect(join(BOT_DATA_DIR, BOT_DB))
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()


def _init_config():
    logger.debug("Initializing configuration database.")
    with _cursor() as cur:
        cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')


def ensure_init(f):
    def wrapper(*args, **kwargs):
        if not state['initialized']:
            _init_config()
            state['initialized'] = True
        return f(*args, **kwargs)

    return wrapper


@ensure_init
def set_key(key, value):
    shown_value = value[:10]
    logger.debug(
        f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
    )
    with _cursor() as cur:
        cur.execute(
            'INSERT INTO config VALUES (?, ?) '
            'ON CONFLICT(key) DO UPDATE SET value=? WHERE key=?',
            (key, value, value, key,),
        )


@ensure_init
def get_key(key):
    logger.debug(f"Getting configuration value for key '{key}'.")
    with _cursor() as cur:
        cur.execute('SELECT value FROM config WHERE key=?', (key,))
        result = cur.fetchone()
    return None if result is None else result[0]
