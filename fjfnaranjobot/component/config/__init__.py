from logging import getLogger
from os.path import join
from sqlite3 import connect

from telegram.ext import CommandHandler

from fjfnaranjobot import BOT_DATA_DIR


logger = getLogger(__name__)


conn = connect(join(BOT_DATA_DIR, 'bot.db'))
cur = conn.cursor()


def config_set_handler_processor(bot, update):
    _, key, value = update.message.text.split(' ')
    logger.info(f"Setting config '{key}' to '{value}'.")
    cur.execute('INSERT INTO config VALUES (?, ?)', (key, value))
    conn.commit()
    

def config_get_handler_processor(bot, update):
    _, key = update.message.text.split(' ')
    cur.execute('SELECT value FROM config WHERE key=?', (key, ))
    result = cur.fetchone()
    if result is None:
        logger.info(f"Replying with 'no value' message for config '{key}'.")
        update.message.reply_text(f"No value for config '{key}'.")
    else:
        value = result[0]
        logger.info(f"Replying with '{value}' for config '{key}'.")
        update.message.reply_text(value)


config_set_handler = CommandHandler('config_set', config_set_handler_processor)
config_get_handler = CommandHandler('config_get', config_get_handler_processor)

logger.info("Initializing settings database.")
cur.execute(
    'CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)'
)
