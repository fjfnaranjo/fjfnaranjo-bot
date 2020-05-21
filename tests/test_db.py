from os import chmod, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from stat import S_IRWXU
from tempfile import mkdtemp, mkstemp
from unittest.mock import patch

from fjfnaranjobot.db import (
    EnvValueError,
    InvalidKeyError,
    _get_db_path,
    cursor,
    get_config,
    reset,
    set_config,
)

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.db'
BOT_DB_NAME_DEFAULT = 'bot.db'
BOT_DB_NAME_TEST = 'bot.a.test.name.db'


class ConfigTests(BotTestCase):
    def setUp(self):
        BotTestCase.setUp(self)
        self._db_test_file = mkstemp()[1]
        self._db_test_dir = mkdtemp()
        self._get_db_path_patcher = patch(f'{MODULE_PATH}._get_db_path')
        self._get_db_path_mock = self._get_db_path_patcher.start()
        self._get_db_path_mock.return_value = self._db_test_file

    def tearDown(self):
        self._get_db_path_patcher.stop()
        self._get_db_path_mock = None
        if isfile(self._db_test_file):
            remove(self._db_test_file)
        if isdir(self._db_test_dir):
            chmod(self._db_test_dir, S_IRWXU)
            rmtree(self._db_test_dir)
        BotTestCase.tearDown(self)

    @patch(f'{MODULE_PATH}.get_bot_data_dir', return_value='dir')
    def test_get_db_path_join_and_default(self, _get_bot_data_dir):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', None, ['BOT_DB_NAME',]
        ):
            assert _get_db_path() == join('dir', BOT_DB_NAME_DEFAULT)

    @patch(f'{MODULE_PATH}.get_bot_data_dir', return_value='dir')
    def test_get_db_path_join_and_env(self, _get_bot_data_dir):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DB_NAME': BOT_DB_NAME_TEST},
        ):
            assert _get_db_path() == join('dir', BOT_DB_NAME_TEST)

    def test_reset_only_reset(self):
        self._get_db_path_mock.return_value = self._db_test_file
        remove(self._db_test_file)
        reset(False)
        assert not isfile(self._db_test_file)

    def test_reset_creates_new(self):
        self._get_db_path_mock.return_value = self._db_test_file
        remove(self._db_test_file)
        reset()
        assert isfile(self._db_test_file)

    def test_reset_replaces_existent(self):
        self._get_db_path_mock.return_value = self._db_test_file
        with open(self._db_test_file, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset()
        with open(self._db_test_file, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    def test_reset_invalid_db_dir_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_file, 'impossibledir')
        with self.assertRaises(EnvValueError) as e:
            reset()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'dir' in str(e.exception)

    def test_reset_invalid_db_file_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_dir, 'dontexists')
        chmod(self._db_test_dir, 0)
        with self.assertRaises(EnvValueError) as e:
            reset()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'file' in str(e.exception)

    def test_cursor_creates_new(self):
        self._get_db_path_mock.return_value = self._db_test_file
        reset(False)
        with cursor() as cur:
            cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
        assert isfile(self._db_test_file)

    def test_cursor_invalid_db_dir_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_file, 'impossibledir')
        reset(False)
        with self.assertRaises(EnvValueError) as e:
            cursor().__enter__()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'dir' in str(e.exception)

    def test_cursor_invalid_db_file_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_dir, 'dontexists')
        reset(False)
        chmod(self._db_test_dir, 0)
        with self.assertRaises(EnvValueError) as e:
            cursor().__enter__()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'file' in str(e.exception)

    def test_cursor_persist(self):
        self._get_db_path_mock.return_value = self._db_test_file
        reset()
        with cursor() as cur:
            cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
            cur.execute('INSERT INTO dummy VALUES (123)')
        with cursor() as cur:
            cur.execute('SELECT key FROM dummy')
            data = cur.fetchall()
        assert 1 == len(data)
        assert 123 == data[0][0]

    def test_get_config_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                get_config(key)

    def test_get_config_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    get_config(key)

    def test_set_config_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                set_config(key, 'val')

    def test_set_config_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    set_config(key, 'val')

    def test_set_config_get_config_persist(self):
        reset()
        set_config('key', 'val')
        val = get_config('key')
        assert 'val' == val

    def test_get_config_dont_exists(self):
        reset()
        val = get_config('key')
        assert None == val

    def test_set_config_replaces_old_value(self):
        reset()
        set_config('key', 'val')
        set_config('key', 'val2')
        val = get_config('key')
        assert 'val2' == val
