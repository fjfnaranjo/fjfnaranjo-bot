from os import environ, makedirs, remove
from os.path import isdir, isfile, split

from fjfnaranjobot.backends.config.sql import SQLConfiguration
from fjfnaranjobot.backends.sqldb.sqlite3 import SQLite3SQLDatabase
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

_BOT_DB_DEFAULT_NAME = ":memory:"


def _ensure_sqldb():
    db_path = environ.get("BOT_DB_NAME", _BOT_DB_DEFAULT_NAME)
    logger.debug(f"Using {db_path} as database.")
    if not db_path.startswith(":"):
        db_dir, _ = split(db_path)
        if not isdir(db_dir):
            try:
                makedirs(db_dir)
            except:
                raise ValueError("Invalid dir name in BOT_DB_NAME var.")
        if not isfile(db_path):
            logger.debug("Creating empty database.")
            try:
                with open(db_path, "wb"):
                    pass
            except OSError:
                raise ValueError("Invalid file name in BOT_DB_NAME var.")
    return SQLite3SQLDatabase(db_path)


sqldb = _ensure_sqldb()

config = SQLConfiguration(sqldb)
