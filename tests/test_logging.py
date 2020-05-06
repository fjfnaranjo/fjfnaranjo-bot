from unittest import TestCase
from unittest.mock import patch

from pytest import raises

from fjfnaranjobot.logging import getLogger, state
from fjfnaranjobot.utils import EnvValueError

MODULE_PATH = 'fjfnaranjobot.logging'

FAKE_LEVEL = 99


class LoggingTests(TestCase):
    def test_logger_no_default_name(self):
        with raises(TypeError):
            getLogger()

    @patch(f'{MODULE_PATH}._BOT_LOGFILE', '/i/dont/exists')
    def test_logger_no_valid_file(self):
        with raises(EnvValueError) as e:
            state['configured'] = False
            getLogger('fbtest')
            assert 'BOT_LOGFILE' in e.msg

    @patch(f'{MODULE_PATH}._BOT_LOGLEVEL', FAKE_LEVEL)
    def test_logger_no_valid_log_level(self):
        with raises(EnvValueError) as e:
            state['configured'] = False
            getLogger('fbtest')
            assert 'BOT_LOGLEVEL' in e.msg

    def test_logger_alt_level(self):
        logger = getLogger('fbtest', FAKE_LEVEL)
        assert logger.getEffectiveLevel() == FAKE_LEVEL
