from logging import getLogger
from os.path import join
from sqlite3 import connect

from fjfnaranjobot.bot import BOT_DATA_DIR


logger = getLogger(__name__)


def init_config():
    logger.info("Initializing settings database.")
    setup_conn = connect(join(BOT_DATA_DIR, 'bot.db'))
    setup_cur = setup_conn.cursor()
    setup_cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')
    setup_cur.close()
    setup_conn.close()


def config_set(bot, update):
    _, key, value = update.message.text.split(' ')
    logger.info(f"Setting config '{key}' to '{value}'.")
    conn = connect(join(BOT_DATA_DIR, 'bot.db'))
    cur = conn.cursor()
    cur.execute('INSERT INTO config VALUES (?, ?)', (key, value))
    conn.commit()


def config_get(bot, update):
    _, key = update.message.text.split(' ')
    conn = connect(join(BOT_DATA_DIR, 'bot.db'))
    cur = conn.cursor()
    cur.execute('SELECT value FROM config WHERE key=?', (key,))
    result = cur.fetchone()
    if result is None:
        logger.info(f"Replying with 'no value' message for config '{key}'.")
        update.message.reply_text(f"No value for config '{key}'.")
    else:
        value = result[0]
        logger.info(f"Replying with '{value}' for config '{key}'.")
        update.message.reply_text(value)
