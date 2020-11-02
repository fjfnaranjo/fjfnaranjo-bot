from contextlib import contextmanager
from os import environ, makedirs, remove
from os.path import isdir, isfile, split
from sqlite3 import connect

from fjfnaranjobot.logging import getLogger

_BOT_DB_DEFAULT_NAME = ':memory:'

logger = getLogger(__name__)

_connection = None


def _ensure_connection():
    global _connection
    if _connection is not None:
        return _connection
    db_path = environ.get('BOT_DB_NAME', _BOT_DB_DEFAULT_NAME)
    if not db_path.startswith(":"):
        db_dir, _ = split(db_path)
        if not isdir(db_dir):
            try:
                makedirs(db_dir)
            except:
                raise ValueError("Invalid dir name in BOT_DB_NAME var.")
        if not isfile(db_path):
            logger.debug("Initializing configuration database.")
            try:
                with open(db_path, 'wb'):
                    pass
            except OSError:
                raise ValueError("Invalid file name in BOT_DB_NAME var.")
    _connection = connect(db_path)
    return _connection


def reset_connection(create=True):
    global _connection
    if _connection is None:
        return
    _connection.close()
    _connection = None
    _ensure_connection()


@contextmanager
def cursor():
    conn = _ensure_connection()
    cur = conn.cursor()
    yield cur
    conn.commit()


# TODO: Test default
class DbField:
    def __init__(self, name, definition=None, default=None):
        self.name = name
        self.definition = definition
        self.default = default


class DbRelation:
    @staticmethod
    def _insert_under_before_upper(class_name):
        for char in enumerate(class_name):
            if char[0] == 0:
                first_lower = class_name[0].lower() + class_name[1:]
                continue
            if char[1].isupper():
                if char[0] == len(first_lower) - 1:
                    return first_lower[: char[0]] + '_' + char[1].lower()
                else:
                    new_class_name = (
                        first_lower[: char[0]]
                        + '_'
                        + char[1].lower()
                        + first_lower[char[0] + 1 :]
                    )
                return DbRelation._insert_under_before_upper(new_class_name)
        return first_lower

    @staticmethod
    @contextmanager
    def _cursor(relation_name, fields):
        with cursor() as cur:
            cur.execute(
                f'CREATE TABLE IF NOT EXISTS {relation_name} ('
                + (
                    ','.join(
                        [
                            field.name
                            + (
                                f' {field.definition}'
                                if field.definition is not None
                                else ''
                            )
                            for field in fields
                        ]
                    )
                )
                + ')'
            )
            yield cur

    def __new__(cls, pk=None):
        new_relation = super().__new__(cls)
        new_relation.relation_name = DbRelation._insert_under_before_upper(cls.__name__)
        for field in cls.fields:
            # TODO: Check default value
            setattr(new_relation, field.name, field.default)
        if pk is not None:
            DbRelation._from_db(
                new_relation, pk, new_relation.relation_name, cls.fields
            )
        return new_relation

    @staticmethod
    def _from_db(instance, pk, relation_name, fields):
        with DbRelation._cursor(relation_name, fields) as cur:
            cur.execute(f'SELECT * FROM {relation_name} WHERE id=?', (pk,))
            values = cur.fetchone()
            if values is None:
                raise RuntimeError(
                    f"Row with id {pk} doesn't exists in relation '{relation_name}'."
                )
            for field in zip(fields, values):
                setattr(instance, field[0].name, field[1])

    def _commit_new(self, cur):
        cur.execute(
            f'INSERT INTO {self.relation_name} VALUES ('
            + ', '.join(['?' for _ in self.fields])
            + ')',
            [getattr(self, field.name) for field in self.fields],
        )
        return cur.lastrowid

    def _commit_replace(self, cur):
        cur.execute(
            f'UPDATE {self.relation_name} SET '
            + ', '.join([f'{field.name}=?' for field in self.fields][1:])
            + ' WHERE id=?',
            [getattr(self, field.name) for field in self.fields[1:]] + [self.id],
        )

    def commit(self):
        with self._cursor(self.relation_name, self.fields) as cur:
            if self.id is not None:
                cur.execute(
                    f'SELECT * FROM {self.relation_name} WHERE id=?', (self.id,)
                )
                values = cur.fetchone()
                if values is None:
                    self.id = self._commit_new(cur)
                else:
                    self._commit_replace(cur)
            else:
                self.id = self._commit_new(cur)

    # TODO: Test
    def delete(self):
        with self._cursor(self.relation_name, self.fields) as cur:
            if self.id is not None:
                cur.execute(f'DELETE FROM {self.relation_name} WHERE id=?', (self.id,))
            else:
                raise ValueError("The db object doesn't have id.")

    @classmethod
    def all(cls):
        all_values = []
        dummy = cls()
        with DbRelation._cursor(dummy.relation_name, cls.fields) as cur:
            cur.execute(f'SELECT * FROM {dummy.relation_name}')
            rows = cur.fetchall()
            for row in rows:
                new_relation = cls()
                for field in zip(cls.fields, row):
                    setattr(new_relation, field[0].name, field[1])
                all_values.append(new_relation)
        for value in all_values:
            yield value

    @classmethod
    def select(cls, **kwargs):
        all_values = []
        dummy = cls()
        with DbRelation._cursor(dummy.relation_name, cls.fields) as cur:
            where_keys = []
            where_values = []
            for key in kwargs:
                where_keys.append(key)
                where_values.append(kwargs[key])
            where_conditions = [f'{key}=?' for key in where_keys]
            where_body = ' AND '.join(where_conditions)
            cur.execute(
                f'SELECT * FROM {dummy.relation_name} WHERE {where_body}', where_values
            )
            rows = cur.fetchall()
            for row in rows:
                relation = cls()
                for field in zip(cls.fields, row):
                    setattr(relation, field[0].name, field[1])
                all_values.append(relation)
            return all_values
