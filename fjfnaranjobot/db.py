from fjfnaranjobot.backends import sqldb
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


# TODO: Test default
class DbField:
    def __init__(self, name, definition=None, default=None):
        self.name = name
        self.definition = definition
        self.default = default


class DbRelation:
    @staticmethod
    def _init_table(relation_name, fields):
        sqldb.execute(
            f"CREATE TABLE IF NOT EXISTS {relation_name} ("
            + (
                ",".join(
                    [
                        field.name
                        + (
                            f" {field.definition}"
                            if field.definition is not None
                            else ""
                        )
                        for field in fields
                    ]
                )
            )
            + ")"
        )

    @staticmethod
    def _insert_under_before_upper(class_name):
        for char in enumerate(class_name):
            if char[0] == 0:
                first_lower = class_name[0].lower() + class_name[1:]
                continue
            if char[1].isupper():
                if char[0] == len(first_lower) - 1:
                    return first_lower[: char[0]] + "_" + char[1].lower()
                else:
                    new_class_name = (
                        first_lower[: char[0]]
                        + "_"
                        + char[1].lower()
                        + first_lower[char[0] + 1 :]
                    )
                return DbRelation._insert_under_before_upper(new_class_name)
        return first_lower

    def __new__(cls, pk=None):
        new_relation = super().__new__(cls)
        relation_name = DbRelation._insert_under_before_upper(cls.__name__)
        DbRelation._init_table(relation_name, cls.fields)
        new_relation.relation_name = relation_name
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
        values = sqldb.execute_and_fetch_one(
            f"SELECT * FROM {relation_name} WHERE id=?", (pk,)
        )
        if values is None:
            raise RuntimeError(
                f"Row with id {pk} doesn't exists in relation '{relation_name}'."
            )
        for field in zip(fields, values):
            setattr(instance, field[0].name, field[1])

    def _commit_new(self):
        return sqldb.execute_and_fetch_index(
            f"INSERT INTO {self.relation_name} VALUES ("
            + ", ".join(["?" for _ in self.fields])
            + ")",
            [getattr(self, field.name) for field in self.fields],
        )

    def _commit_replace(self):
        sqldb.execute(
            f"UPDATE {self.relation_name} SET "
            + ", ".join([f"{field.name}=?" for field in self.fields][1:])
            + " WHERE id=?",
            [getattr(self, field.name) for field in self.fields[1:]] + [self.id],
        )

    def commit(self):
        if self.id is not None:
            values = sqldb.execute_and_fetch_one(
                f"SELECT * FROM {self.relation_name} WHERE id=?", (self.id,)
            )
            if values is None:
                self.id = self._commit_new()
            else:
                self._commit_replace()
        else:
            self.id = self._commit_new()

    # TODO: Test
    def delete(self):
        if self.id is not None:
            sqldb.execute(f"DELETE FROM {self.relation_name} WHERE id=?", (self.id,))
        else:
            raise ValueError("The db object doesn't have id.")

    @classmethod
    def all(cls):
        all_values = []
        dummy = cls()
        rows = sqldb.execute_and_fetch_all(f"SELECT * FROM {dummy.relation_name}")
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
        where_keys = []
        where_values = []
        for key in kwargs:
            where_keys.append(key)
            where_values.append(kwargs[key])
        where_conditions = [f"{key}=?" for key in where_keys]
        where_body = " AND ".join(where_conditions)
        rows = sqldb.execute_and_fetch_all(
            f"SELECT * FROM {dummy.relation_name} WHERE {where_body}", where_values
        )
        for row in rows:
            relation = cls()
            for field in zip(cls.fields, row):
                setattr(relation, field[0].name, field[1])
            all_values.append(relation)
        return all_values
