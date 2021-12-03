from contextlib import contextmanager
from sqlite3 import connect

from fjfnaranjobot.backends.sqldb.interface import SQLDatabase


class SQLite3SQLDatabase(SQLDatabase):
    def __init__(self, path):
        self.connection = connect(path)

    @contextmanager
    def _sqlite3_cursor(self):
        cursor = self.connection.cursor()
        yield cursor
        self.connection.commit()
        cursor.close()

    def execute(self, sentence, *params):
        with self._sqlite3_cursor() as cursor:
            cursor.execute(sentence, *params)

    def execute_and_fetch_index(self, sentence, *params):
        with self._sqlite3_cursor() as cursor:
            cursor.execute(sentence, *params)
            lastrowid = cursor.lastrowid
        return lastrowid

    def execute_and_fetch_one(self, sentence, *params):
        with self._sqlite3_cursor() as cursor:
            return cursor.execute(sentence, *params).fetchone()

    def execute_and_fetch_all(self, sentence, *params):
        with self._sqlite3_cursor() as cursor:
            return cursor.execute(sentence, *params).fetchall()
