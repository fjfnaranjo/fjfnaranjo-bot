from unittest import TestCase
from unittest.mock import patch

from fjfnaranjobot.utils import get_bot_data_dir

MODULE_PATH = 'fjfnaranjobot.utils'
BOT_DATA_DIR_DEFAULT = 'botdata'
BOT_DATA_DIR_TEST = '/bot/data/test'


class UtilsTests(TestCase):
    @patch.dict(f'{MODULE_PATH}.environ', {}, True)
    def test_get_bot_data_dir_default(self):
        assert get_bot_data_dir() == BOT_DATA_DIR_DEFAULT

    @patch.dict(f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': BOT_DATA_DIR_TEST})
    def test_get_bot_data_dir_env(self):
        assert get_bot_data_dir() == BOT_DATA_DIR_TEST
