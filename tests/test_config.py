from os import chmod, remove
from os.path import isdir, isfile, join
from shutil import rmtree
from stat import S_IRWXU
from tempfile import mkdtemp, mkstemp
from unittest.mock import patch

from fjfnaranjobot.config import (
    EnvValueError,
    InvalidKeyError,
    _get_db_path,
    cursor,
    get_key,
    reset_state,
    set_key,
)

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.config'
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

    def test_reset_state_only_reset(self):
        self._get_db_path_mock.return_value = self._db_test_file
        remove(self._db_test_file)
        reset_state(False)
        assert not isfile(self._db_test_file)

    def test_reset_state_creates_new(self):
        self._get_db_path_mock.return_value = self._db_test_file
        remove(self._db_test_file)
        reset_state()
        assert isfile(self._db_test_file)

    def test_reset_state_replaces_existent(self):
        self._get_db_path_mock.return_value = self._db_test_file
        with open(self._db_test_file, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset_state()
        with open(self._db_test_file, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    def test_reset_state_invalid_db_dir_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_file, 'impossibledir')
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'dir' in str(e.exception)

    def test_reset_state_invalid_db_file_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_dir, 'dontexists')
        chmod(self._db_test_dir, 0)
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'file' in str(e.exception)

    def test_cursor_creates_new(self):
        self._get_db_path_mock.return_value = self._db_test_file
        reset_state(False)
        with cursor() as cur:
            cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
        assert isfile(self._db_test_file)

    def test_cursor_invalid_db_dir_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_file, 'impossibledir')
        reset_state(False)
        with self.assertRaises(EnvValueError) as e:
            with cursor() as cur:
                cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'dir' in str(e.exception)

    def test_cursor_invalid_db_file_name(self):
        self._get_db_path_mock.return_value = join(self._db_test_dir, 'dontexists')
        reset_state(False)
        chmod(self._db_test_dir, 0)
        with self.assertRaises(EnvValueError) as e:
            with cursor() as cur:
                cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'file' in str(e.exception)

    def test_cursor_persist(self):
        self._get_db_path_mock.return_value = self._db_test_file
        reset_state()
        with cursor() as cur:
            cur.execute('CREATE TABLE dummy (key PRIMARY KEY)')
            cur.execute('INSERT INTO dummy VALUES (123)')
        with cursor() as cur:
            cur.execute('SELECT key FROM dummy')
            data = cur.fetchall()
        assert 1 == len(data)
        assert 123 == data[0][0]

    def test_get_key_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                get_key(key)

    def test_get_key_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    get_key(key)

    def test_set_key_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                set_key(key, 'val')

    def test_set_key_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    set_key(key, 'val')

    def test_set_key_get_key_persist(self):
        reset_state()
        set_key('key', 'val')
        val = get_key('key')
        assert 'val' == val

    def test_get_key_dont_exists(self):
        reset_state()
        val = get_key('key')
        assert None == val

    def test_set_key_replaces_old_value(self):
        reset_state()
        set_key('key', 'val')
        set_key('key', 'val2')
        val = get_key('key')
        assert 'val2' == val
