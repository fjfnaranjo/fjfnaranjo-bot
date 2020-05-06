from os.path import join
from tempfile import mktemp
from unittest import TestCase
from unittest.mock import patch

from pytest import raises

from fjfnaranjobot.config import (
    EnvValueError,
    get_db_path,
    get_key,
    reset_state,
    set_key,
)

MODULE_PATH = 'fjfnaranjobot.config'
BOT_DB_NAME_DEFAULT = 'bot.db'
BOT_DB_NAME_TEST = 'bot.a.test.name.db'
DB_TEST_FILE = mktemp()


class ConfigTests(TestCase):
    @patch.dict(f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': 'dir'}, True)
    def test_get_db_path_join_and_default(self):
        assert get_db_path() == join('dir', BOT_DB_NAME_DEFAULT)

    @patch.dict(
        f'{MODULE_PATH}.environ',
        {'BOT_DATA_DIR': 'dir', 'BOT_DB_NAME': BOT_DB_NAME_TEST},
    )
    def test_get_db_path_join_and_env(self):
        assert get_db_path() == join('dir', BOT_DB_NAME_TEST)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_reset_state_creates_new(self, _get_db_path):
        with open(DB_TEST_FILE, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset_state()
        with open(DB_TEST_FILE, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    @patch(f'{MODULE_PATH}.get_db_path', return_value='/dev/not-a-valid-dir/a')
    def test_reset_state_invalid_db_dir_name(self, _get_db_path):
        with raises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e)
        assert 'dir' in str(e)

    @patch(f'{MODULE_PATH}.get_db_path', return_value='/dev/not-a-valid-name')
    def test_reset_state_invalid_db_file_name(self, _get_db_path):
        with raises(EnvValueError) as e:
            reset_state()
        assert 'BOT_DB_NAME' in str(e)
        assert 'file' in str(e)

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_store_set_get_value(self, _get_db_path):
        reset_state()
        set_key('key', 'val')
        val = get_key('key')
        assert 'val' == val

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_retrieve_get_value_dont_exists(self, _get_db_path):
        reset_state()
        val = get_key('key')
        assert None == val

    @patch(f'{MODULE_PATH}.get_db_path', return_value=DB_TEST_FILE)
    def test_store_set_existing_get_value(self, _get_db_path):
        reset_state()
        set_key('key', 'val')
        set_key('key', 'val2')
        val = get_key('key')
        assert 'val2' == val

    # TODO: Independent access to DB
