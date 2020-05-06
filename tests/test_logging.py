from os.path import isfile, join
from tempfile import mktemp
from unittest import TestCase
from unittest.mock import patch

from pytest import raises

from fjfnaranjobot.logging import get_log_path, getLogger, reset_state
from fjfnaranjobot.utils import EnvValueError

MODULE_PATH = 'fjfnaranjobot.logging'
BOT_LOGFILE_DEFAULT = 'bot.log'
BOT_LOGFILE_TEST = 'bot.a.test.name.log'
LOGFILE_TEST_FILE = mktemp()
FAKE_LEVEL = 99


class LoggingTests(TestCase):
    @patch.dict(f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': 'dir'}, True)
    def test_get_log_path_join_and_default(self):
        assert get_log_path() == join('dir', BOT_LOGFILE_DEFAULT)

    @patch.dict(
        f'{MODULE_PATH}.environ',
        {'BOT_DATA_DIR': 'dir', 'BOT_LOGFILE': BOT_LOGFILE_TEST},
    )
    def test_get_log_path_join_and_env(self):
        assert get_log_path() == join('dir', BOT_LOGFILE_TEST)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_reset_state_creates_new(self, _get_log_path):
        with open(LOGFILE_TEST_FILE, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset_state()
        with open(LOGFILE_TEST_FILE, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    @patch(f'{MODULE_PATH}.get_log_path', return_value='/dev/not-a-valid-dir/a')
    def test_reset_state_invalid_log_dir_name(self, _get_log_path):
        with raises(EnvValueError) as e:
            reset_state()
        assert 'BOT_LOGFILE' in str(e)
        assert 'dir' in str(e)

    @patch(f'{MODULE_PATH}.get_log_path', return_value='/dev/not-a-valid-name')
    def test_reset_state_invalid_db_file_name(self, _get_log_path):
        with raises(EnvValueError) as e:
            reset_state()
        assert 'BOT_LOGFILE' in str(e)
        assert 'file' in str(e)

    @patch.dict(f'{MODULE_PATH}.environ', {'BOT_LOGLEVEL': f'{FAKE_LEVEL}'}, True)
    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_no_valid_log_level(self, _get_log_path):
        with raises(EnvValueError) as e:
            reset_state()
            getLogger('fbtest')
        assert 'BOT_LOGLEVEL' in str(e)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_no_default_name(self, _get_log_path):
        with raises(TypeError):
            getLogger()

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_init_log(self, _get_log_path):
        reset_state()
        assert isfile(LOGFILE_TEST_FILE)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_alt_level(self, _get_log_path):
        logger = getLogger('fbtest', FAKE_LEVEL)
        assert logger.getEffectiveLevel() == FAKE_LEVEL
