from os import chmod
from os.path import join
from tempfile import mkdtemp, mkstemp
from unittest.mock import patch

from fjfnaranjobot.config import (
    EnvValueError,
    InvalidKeyError,
    get_db_path,
    get_key,
    reset_state,
    set_key,
)

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.config'
BOT_DB_NAME_DEFAULT = 'bot.db'
BOT_DB_NAME_TEST = 'bot.a.test.name.db'
DB_TEST_FILE = mkstemp()[1]
DB_TEST_DIR = mkdtemp()


class ConfigTests(BotTestCase):
    def test_get_db_path_join_and_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': 'dir'}, ['BOT_DB_NAME'],
        ):
            assert get_db_path() == join('dir', BOT_DB_NAME_DEFAULT)

    def test_get_db_path_join_and_env(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ',
            {'BOT_DATA_DIR': 'dir', 'BOT_DB_NAME': BOT_DB_NAME_TEST},
        ):
            assert get_db_path() == join('dir', BOT_DB_NAME_TEST)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_reset_state_creates_new(self, _get_db_path):
        with open(DB_TEST_FILE, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset_state()
        with open(DB_TEST_FILE, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    @patch(f'{MODULE_PATH}.get_db_path', return_value=join(DB_TEST_FILE, 'dir'))
    def test_reset_state_invalid_db_dir_name(self, _get_db_path):
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'dir' in str(e.exception)

    @patch(
        f'{MODULE_PATH}.get_db_path', return_value=join(DB_TEST_DIR, 'file'),
    )
    def test_reset_state_invalid_db_file_name(self, _get_db_path):
        chmod(DB_TEST_DIR, 0)
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e.exception)
        assert 'file' in str(e.exception)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_get_key_valid(self, _get_db_path):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                get_key(key)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_get_key_invalid(self, _get_db_path):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    get_key(key)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_set_key_valid(self, _get_db_path):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                set_key(key, 'val')

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_set_key_invalid(self, _get_db_path):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError):
                    set_key(key, 'val')

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_set_get_key(self, _get_db_path):
        reset_state()
        set_key('key', 'val')
        val = get_key('key')
        assert 'val' == val

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_get_key_dont_exists(self, _get_db_path):
        reset_state()
        val = get_key('key')
        assert None == val

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_set_key_get_value(self, _get_db_path):
        reset_state()
        set_key('key', 'val')
        set_key('key', 'val2')
        val = get_key('key')
        assert 'val2' == val
