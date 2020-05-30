from fjfnaranjobot.common import get_bot_data_dir

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.bot'
BOT_DATA_DIR_DEFAULT = 'botdata'
BOT_DATA_DIR_TEST = '/bot/data/test'


class BotUtilsTests(BotTestCase):
    def test_get_bot_data_dir_default(self):
        with self.mocked_environ(f'{MODULE_PATH}.environ', None, ['BOT_DATA_DIR']):
            assert get_bot_data_dir() == BOT_DATA_DIR_DEFAULT

    def test_get_bot_data_dir_env(self):
        with self.mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': BOT_DATA_DIR_TEST}
        ):
            assert get_bot_data_dir() == BOT_DATA_DIR_TEST
