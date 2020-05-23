from contextlib import contextmanager
from re import compile

from fjfnaranjobot.db import cursor
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class InvalidKeyError(Exception):
    pass


def _validate_key(key):
    validator = compile(r'^([a-zA-Z]+\.)*([a-zA-Z]+)+$')
    if validator.fullmatch(key) is None:
        raise InvalidKeyError(f"No valid value for key {key}.")


@contextmanager
def _config_cursor():
    with cursor() as cur:
        cur.execute('CREATE TABLE IF NOT EXISTS config (key PRIMARY KEY, value)')
        yield cur


def reset():
    with cursor() as cur:
        cur.execute('DELETE FROM config')


def set_config(key, value):
    _validate_key(key)
    shown_value = value[:10]
    logger.debug(
        f"Setting configuration key '{key}' to value '{shown_value}' (cropped to 10 chars)."
    )
    with _config_cursor() as cur:
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


def get_config(key):
    _validate_key(key)
    logger.debug(f"Getting configuration value for key '{key}'.")
    with _config_cursor() as cur:
        cur.execute('SELECT value FROM config WHERE key=?', (key,))
        result = cur.fetchone()
    if result is None:
        raise KeyError(f"The key '{key}' don't exists.")
    else:
        return result[0]
