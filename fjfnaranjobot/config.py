from collections.abc import MutableMapping
from contextlib import contextmanager
from re import compile

from fjfnaranjobot.db import cursor
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class _ConfigurationProxy(MutableMapping):
    @staticmethod
    def _validate_key(key):
        validator = compile(r'^([a-zA-Z]+\.)*([a-zA-Z]+)+$')
        if validator.fullmatch(key) is None:
            raise ValueError(f"No valid value for key {key}.")

    @staticmethod
    @contextmanager
    def _config_cursor():
        with cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')
            yield cur

    def __getitem__(self, key):
        self._validate_key(key)
        logger.debug(f"Getting configuration value for key '{key}'.")
        with self._config_cursor() as cur:
            cur.execute('SELECT value FROM config WHERE key=?', (key,))
            result = cur.fetchone()
        if result is None:
            raise KeyError(f"The key '{key}' don't exists.")
        else:
            return result[0]

    def __setitem__(self, key, value):
        self._validate_key(key)
        shown_value = value[:10] if value is not None else 'None'
        logger.debug(
            f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
        )
        with self._config_cursor() as cur:
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

    def __delitem__(self, key):
        self._validate_key(key)
        if key not in self:
            raise KeyError(f"The key '{key}' don't exists.")
        logger.debug(f"Deleting configuration key '{key}'.")
        with self._config_cursor() as cur:
            cur.execute('DELETE FROM config WHERE key=?', (key,))

    def __len__(self):
        with self._config_cursor() as cur:
            cur.execute('SELECT count(*) FROM config')
            return cur.fetchone()[0]

    def __iter__(self):
        with self._config_cursor() as cur:
            cur.execute('SELECT key FROM config')
            all_keys = cur.fetchall()
        for item in all_keys:
            yield item[0]


config = _ConfigurationProxy()
