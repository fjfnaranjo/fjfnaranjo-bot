from logging import DEBUG
from os import chmod, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from sqlite3 import OperationalError
from stat import S_IRWXU
from tempfile import mkdtemp, mkstemp
from unittest.mock import MagicMock, patch

from fjfnaranjobot.db import DbField, DbRelation, cursor, logger, reset_connection

from .base import BotTestCase

MODULE_PATH = "fjfnaranjobot.db"


class DbMemoryTests(BotTestCase):
    def run(self, *args, **kwargs):
        with self.mocked_environ(f"{MODULE_PATH}.environ", {"BOT_DB_NAME": ":memory:"}):
            return super().run(*args, **kwargs)


class DbResetTests(DbMemoryTests):
    def test_reset_clear_data(self):
        reset_connection()
        with cursor() as cur:
            cur.execute("CREATE TABLE dummy (key PRIMARY KEY)")
        reset_connection()
        with cursor() as cur:
            with self.assertRaises(OperationalError):
                cur.execute("SELECT * FROM dummy;")


class DbPathTests(BotTestCase):
    def setUp(self):
        super().setUp()
        self._db_test_file = mkstemp()[1]
        self._db_test_dir = mkdtemp()

    def tearDown(self):
        if isfile(self._db_test_file):
            remove(self._db_test_file)
        if isdir(self._db_test_dir):
            chmod(self._db_test_dir, S_IRWXU)
            rmtree(self._db_test_dir)
        BotTestCase.tearDown(self)

    def test_path_valid_db_name(self):
        valid_path = join(self._db_test_dir, "valid")
        with self.mocked_environ(f"{MODULE_PATH}.environ", {"BOT_DB_NAME": valid_path}):
            reset_connection()
            with cursor() as cur:
                cursor().__enter__()
        assert isfile(valid_path)

    def test_path_valid_db_name_create_dir(self):
        valid_path = join(self._db_test_dir, "dir", "valid")
        with self.mocked_environ(f"{MODULE_PATH}.environ", {"BOT_DB_NAME": valid_path}):
            reset_connection()
            with cursor() as cur:
                cursor().__enter__()
        assert isfile(valid_path)

    def test_path_invalid_db_dir_name(self):
        invalid_path = join(self._db_test_file, "irrelevant")
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_DB_NAME": invalid_path}
        ):
            with self.assertRaises(ValueError) as e:
                reset_connection()
        assert "Invalid dir name in BOT_DB_NAME var." == e.exception.args[0]

    def test_path_invalid_db_file_name(self):
        invalid_path = join(self._db_test_dir, "irrelevant")
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_DB_NAME": invalid_path}
        ):
            chmod(self._db_test_dir, 0)
            with self.assertRaises(ValueError) as e:
                reset_connection()
                cursor().__enter__()
        assert "Invalid file name in BOT_DB_NAME var." == e.exception.args[0]


class DbTests(DbMemoryTests):
    def setUp(self):
        super().setUp()
        reset_connection()


class DbCursorTests(DbTests):
    def test_cursor(self):
        with cursor() as cur:
            cur.execute("CREATE TABLE dummy (key PRIMARY KEY);")
            cur.execute("INSERT INTO dummy VALUES (1);")
            table = cur.execute("SELECT * FROM dummy").fetchone()
            assert table[0] == 1


class DbRelationMock(DbRelation):
    fields = [
        DbField("id", "INTEGER PRIMARY KEY"),
        DbField("field1", "INTEGER"),
        DbField("field2"),
    ]


class A(DbRelation):
    fields = [
        DbField("id", "INTEGER PRIMARY KEY"),
    ]


class DbRelationEndingUpperMockA(DbRelation):
    fields = [
        DbField("id", "INTEGER PRIMARY KEY"),
    ]


class DbObjectsTests(DbTests):
    def test_db_field(self):
        field = DbField("a", "b")
        assert "a" == field.name
        assert "b" == field.definition

    def test_db_object_relation_name(self):
        new_object = DbRelationMock()
        assert "db_relation_mock" == new_object.relation_name

    def test_db_object_relation_name_single(self):
        new_object = A()
        assert "a" == new_object.relation_name

    def test_db_object_relation_name_ending_upper(self):
        new_object = DbRelationEndingUpperMockA()
        assert "db_relation_ending_upper_mock_a" == new_object.relation_name

    def test_db_object_creates_table(self):
        new_object = DbRelationMock()
        new_object.commit()
        with cursor() as cur:
            cur.execute("select name, sql from sqlite_master where type='table'")
            values = cur.fetchone()
            create_statement = values[1]
            fields_section = create_statement[
                create_statement.find("(") + 1 : create_statement.find(")")
            ]
            fields = fields_section.split(",")
            assert "db_relation_mock" == values[0]
            assert 3 == len(fields)
            assert "id INTEGER PRIMARY KEY" in fields
            assert "field1 INTEGER" in fields
            assert "field2" in fields

    def test_object_dont_exists(self):
        with self.assertRaises(RuntimeError) as e:
            DbRelationMock(1)
        assert (
            "Row with id 1 doesn't exists in relation 'db_relation_mock'."
            == e.exception.args[0]
        )

    def test_object_create_with_id(self):
        new_object = DbRelationMock()
        new_object.id = 1
        new_object.field1 = 0
        new_object.commit()
        del new_object
        created_object = DbRelationMock(1)
        assert 0 == created_object.field1

    def test_object_persist(self):
        new_object = DbRelationMock()
        new_object.field1 = 0
        new_object.commit()
        new_object_pk = new_object.id
        del new_object
        created_object = DbRelationMock(new_object_pk)
        assert 0 == created_object.field1
        assert None == created_object.field2

    def test_object_replace_existing(self):
        new_object = DbRelationMock()
        new_object.field1 = 0
        new_object.commit()
        new_object_pk = new_object.id
        del new_object
        created_object = DbRelationMock(new_object_pk)
        created_object.field1 = 1
        created_object.field2 = "f"
        created_object.commit()
        del created_object
        replaced_object = DbRelationMock(new_object_pk)
        assert 1 == replaced_object.field1
        assert "f" == replaced_object.field2

    def test_object_all(self):
        new_object1 = DbRelationMock()
        new_object1.field1 = 0
        new_object1.field2 = "new_object1"
        new_object1.commit()
        del new_object1
        new_object2 = DbRelationMock()
        new_object2.field1 = 1
        new_object2.field2 = "new_object2"
        new_object2.commit()
        del new_object2
        new_object3 = DbRelationMock()
        new_object3.field1 = 2
        new_object3.field2 = "new_object3"
        new_object3.commit()
        del new_object3

        all_objects = list(DbRelationMock.all())
        assert 3 == len(all_objects)
        assert 0 == all_objects[0].field1
        assert "new_object1" == all_objects[0].field2
        assert 1 == all_objects[1].field1
        assert "new_object2" == all_objects[1].field2
        assert 2 == all_objects[2].field1
        assert "new_object3" == all_objects[2].field2

    def test_object_select(self):
        new_object1 = DbRelationMock()
        new_object1.field1 = 0
        new_object1.field2 = "me"
        new_object1.commit()
        del new_object1
        new_object2 = DbRelationMock()
        new_object2.field1 = 1
        new_object2.field2 = "me"
        new_object2.commit()
        del new_object2
        new_object3 = DbRelationMock()
        new_object3.field1 = 2
        new_object3.field2 = "new_object3"
        new_object3.commit()
        del new_object3

        selected_objects = list(DbRelationMock.select(field2="me"))
        assert 2 == len(selected_objects)
        assert 0 == selected_objects[0].field1
        assert 1 == selected_objects[1].field1
