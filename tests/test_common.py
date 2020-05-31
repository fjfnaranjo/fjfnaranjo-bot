from fjfnaranjobot.common import User, get_bot_data_dir

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.bot'
BOT_DATA_DIR_DEFAULT = 'botdata'
BOT_DATA_DIR_TEST = '/bot/data/test'


class BotDataDirTests(BotTestCase):
    def test_get_bot_data_dir_default(self):
        with self.mocked_environ(f'{MODULE_PATH}.environ', None, ['BOT_DATA_DIR']):
            assert get_bot_data_dir() == BOT_DATA_DIR_DEFAULT

    def test_get_bot_data_dir_env(self):
        with self.mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': BOT_DATA_DIR_TEST}
        ):
            assert get_bot_data_dir() == BOT_DATA_DIR_TEST


class UserTestCase(BotTestCase):
    def test_create_friend(self):
        friend = User(0, 'a')
        assert 0 == friend.id
        assert 'a' == friend.username

    def test_create_friend_not_int(self):
        with self.assertRaises(ValueError):
            User('i', 'a')
