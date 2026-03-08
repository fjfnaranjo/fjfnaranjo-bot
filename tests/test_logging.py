from fjfnaranjobot.logging import getLogger, reset_logging

from .base import MockedEnvironTestCase

MODULE_PATH = "fjfnaranjobot.logging"

FAKE_LEVEL = 99


class LoggingTests(MockedEnvironTestCase):
    def test_logger_no_valid_log_level(self):
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_LOGLEVEL": f"{FAKE_LEVEL}"}
        ):
            with self.assertRaises(ValueError) as e:
                reset_logging()
                getLogger("fbtest")
            assert "Invalid level in BOT_LOGLEVEL var." == e.exception.args[0]

    def test_logger_alt_level(self):
        logger = getLogger("fbtest", FAKE_LEVEL)
        assert logger.getEffectiveLevel() == FAKE_LEVEL
