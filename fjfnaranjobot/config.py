from os import environ
from os.path import join
from sqlite3 import connect

from fjfnaranjobot.logging import getLogger


BOT_DATA_DIR = environ.get('BOT_DATA_DIR', '')
BOT_DB = environ.get('BOT_DB', 'bot.db')

logger = getLogger(__name__)

state = {'initialized': False}


def _init_config():
    logger.debug("Initializing configuration database.")
    setup_conn = connect(join(BOT_DATA_DIR, BOT_DB))
    setup_cur = setup_conn.cursor()
    setup_cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')
    setup_cur.close()
    setup_conn.close()


def set_key(key, value):
    if not state['initialized']:
        _init_config()
        state['initialized'] = True
    shown_value = value[:10]
    logger.debug(
        f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
    )
    conn = connect(join(BOT_DATA_DIR, BOT_DB))
    cur = conn.cursor()
    cur.execute('UPDATE config SET value=? WHERE key=?', (value, key))
    conn.commit()
    cur.close()
    conn.close()


def get_key(key):
    if not state['initialized']:
        _init_config()
        state['initialized'] = True
    logger.debug(f"Getting configuration value for key '{key}'.")
    conn = connect(join(BOT_DATA_DIR, BOT_DB))
    cur = conn.cursor()
    cur.execute('SELECT value FROM config WHERE key=?', (key,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return None if result is None else result[0]
