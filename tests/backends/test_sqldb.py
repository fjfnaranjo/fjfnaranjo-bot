from os import chmod, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from stat import S_IRWXU
from tempfile import mkdtemp, mkstemp
from unittest.mock import patch

from fjfnaranjobot.backends import _ensure_sqldb
from tests.base import MockedEnvironTestCase

MODULE_PATH = "fjfnaranjobot.backends"


class SQLite3SQLDatabaseMock:
    def __init__(self, db_path):
        with open(db_path, "wb"):
            pass


@patch(f"{MODULE_PATH}.SQLite3SQLDatabase", SQLite3SQLDatabaseMock)
class EnsureDbTests(MockedEnvironTestCase):
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
        MockedEnvironTestCase.tearDown(self)

    def test_path_valid_db_name(self):
        valid_path = join(self._db_test_dir, "valid")
        with self.mocked_environ(f"{MODULE_PATH}.environ", {"BOT_DB_NAME": valid_path}):
            _ensure_sqldb()
        assert isfile(valid_path)

    def test_path_valid_db_name_create_dir(self):
        valid_path = join(self._db_test_dir, "dir", "valid")
        with self.mocked_environ(f"{MODULE_PATH}.environ", {"BOT_DB_NAME": valid_path}):
            _ensure_sqldb()
        assert isfile(valid_path)

    def test_path_invalid_db_dir_name(self):
        invalid_path = join(self._db_test_file, "irrelevant")
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_DB_NAME": invalid_path}
        ):
            with self.assertRaises(ValueError) as e:
                _ensure_sqldb()
        assert "Invalid dir name in BOT_DB_NAME var." == e.exception.args[0]

    def test_path_invalid_db_file_name(self):
        invalid_path = join(self._db_test_dir, "irrelevant")
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_DB_NAME": invalid_path}
        ):
            chmod(self._db_test_dir, 0)
            with self.assertRaises(ValueError) as e:
                _ensure_sqldb()
        assert "Invalid file name in BOT_DB_NAME var." == e.exception.args[0]
