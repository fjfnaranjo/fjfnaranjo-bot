from re import compile

from fjfnaranjobot.backends.config.interface import Configuration
from fjfnaranjobot.backends.sqldb.interface import SQLDatabase
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

MAX_KEY_LENGHT = 16


class SQLConfiguration(Configuration):
    def __init__(self, sqldb: SQLDatabase):
        self.sqldb = sqldb
        self.sqldb.execute("CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)")

    @staticmethod
    def _validate_key(key):
        validator = compile(r"^([a-zA-Z]+\.)*([a-zA-Z]+)+$")
        if validator.fullmatch(key) is None or len(key) > MAX_KEY_LENGHT:
            raise ValueError(f"No valid value for key {key}.")

    def __getitem__(self, key):
        self._validate_key(key)
        logger.debug(f"Getting configuration value for key '{key}'.")
        result = self.sqldb.execute_and_fetch_one(
            "SELECT value FROM config WHERE key=?", (key,)
        )
        if result is None:
            raise KeyError(f"The key '{key}' don't exists.")
        else:
            return result[0]

    def __setitem__(self, key, value):
        self._validate_key(key)
        shown_value = value[:10] if value is not None else "None"
        logger.debug(
            f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
        )
        exists = self.sqldb.execute_and_fetch_one(
            "SELECT value FROM config WHERE key=?", (key,)
        )
        if exists is None:
            self.sqldb.execute(
                "INSERT INTO config VALUES (?, ?) ",
                (key, value),
            )
        else:
            self.sqldb.execute(
                "UPDATE config SET key=?, value=? WHERE key=?",
                (key, value, key),
            )

    def __delitem__(self, key):
        self._validate_key(key)
        if key not in self:
            raise KeyError(f"The key '{key}' don't exists.")
        logger.debug(f"Deleting configuration key '{key}'.")
        self.sqldb.execute("DELETE FROM config WHERE key=?", (key,))

    def __len__(self):
        return self.sqldb.execute_and_fetch_one("SELECT count(*) FROM config")[0]

    def __iter__(self):
        all_keys = self.sqldb.execute_and_fetch_all("SELECT key FROM config")
        for key in all_keys:
            yield key[0]
