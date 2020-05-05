from unittest import TestCase
from unittest.mock import patch

from pytest import raises

from fjfnaranjobot.logging import getLogger, state


FAKE_LEVEL = 99


class LoggingTests(TestCase):
    def test_logger_no_default_name(self):
        with raises(TypeError):
            getLogger()

    @patch('fjfnaranjobot.logging.BOT_LOGFILE', '/i/dont/exists')
    def test_logger_no_valid_file(self):
        with raises(ValueError):
            state['configured'] = False
            getLogger('fbtest')

    @patch('fjfnaranjobot.logging.BOT_LOGLEVEL', FAKE_LEVEL)
    def test_logger_no_valid_log_level(self):
        with raises(ValueError):
            state['configured'] = False
            getLogger('fbtest')

    def test_logger_alt_level(self):
        logger = getLogger('fbtest', FAKE_LEVEL)
        assert logger.getEffectiveLevel() == FAKE_LEVEL
