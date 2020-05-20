from os import chmod
from os.path import isfile, join
from tempfile import mkdtemp, mkstemp
from unittest.mock import patch

from fjfnaranjobot.logging import get_log_path, getLogger, reset_state
from fjfnaranjobot.utils import EnvValueError

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.logging'
BOT_LOGFILE_DEFAULT = 'bot.log'
BOT_LOGFILE_TEST = 'bot.a.test.name.log'
LOGFILE_TEST_FILE = mkstemp()[1]
LOGFILE_TEST_DIR = mkdtemp()
FAKE_LEVEL = 99


class LoggingTests(BotTestCase):
    def test_get_log_path_join_and_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': 'dir'}, ['BOT_LOGFILE']
        ):
            assert get_log_path() == join('dir', BOT_LOGFILE_DEFAULT)

    def test_get_log_path_join_and_env(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ',
            {'BOT_DATA_DIR': 'dir', 'BOT_LOGFILE': BOT_LOGFILE_TEST},
        ):
            assert get_log_path() == join('dir', BOT_LOGFILE_TEST)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_reset_state_creates_new(self, _get_log_path):
        with open(LOGFILE_TEST_FILE, 'wb') as temp_file:
            temp_file.write(b'notempty')
        reset_state()
        with open(LOGFILE_TEST_FILE, 'rb') as temp_file:
            assert temp_file.read() != b'notempty'

    @patch(f'{MODULE_PATH}.get_log_path', return_value=join(LOGFILE_TEST_FILE, 'dir'))
    def test_reset_state_invalid_log_dir_name(self, _get_log_path):
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_LOGFILE' in str(e.exception)
        assert 'dir' in str(e.exception)

    @patch(
        f'{MODULE_PATH}.get_log_path', return_value=join(LOGFILE_TEST_DIR, 'file'),
    )
    def test_reset_state_invalid_db_file_name(self, _get_log_path):
        chmod(LOGFILE_TEST_DIR, 0)
        with self.assertRaises(EnvValueError) as e:
            reset_state()
        assert 'BOT_LOGFILE' in str(e.exception)
        assert 'file' in str(e.exception)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_no_valid_log_level(self, _get_log_path):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_LOGLEVEL': f'{FAKE_LEVEL}'}
        ):
            with self.assertRaises(EnvValueError) as e:
                reset_state()
                getLogger('fbtest')
            assert 'BOT_LOGLEVEL' in str(e.exception)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_no_default_name(self, _get_log_path):
        with self.assertRaises(TypeError):
            getLogger()

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_init_log(self, _get_log_path):
        reset_state()
        assert isfile(LOGFILE_TEST_FILE)

    @patch(f'{MODULE_PATH}.get_log_path', return_value=LOGFILE_TEST_FILE)
    def test_logger_alt_level(self, _get_log_path):
        logger = getLogger('fbtest', FAKE_LEVEL)
        assert logger.getEffectiveLevel() == FAKE_LEVEL
