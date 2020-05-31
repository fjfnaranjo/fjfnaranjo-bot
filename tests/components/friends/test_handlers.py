from unittest.mock import patch

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import User
from fjfnaranjobot.components.friends.handlers import friends_handler  # , logger

from ...base import (  # FIRST_FRIEND_USER,; SECOND_FRIEND_USER,; THIRD_FRIEND_USER,
    BotHandlerTestCase,
)

MODULE_PATH = 'fjfnaranjobot.components.friends.handlers'


class FriendsHandlersTests(BotHandlerTestCase):
    def setUp(self):
        BotHandlerTestCase.setUp(self)
        self.user_is_owner()
        self._friends_patcher = patch(f'{MODULE_PATH}.friends', {})
        self._friends_mock = self._friends_patcher.start()
        self.addCleanup(self._friends_patcher.stop)

    def test_config_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_config_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_config_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def friends(self, friend_list):
        for friend in friend_list:
            self._friends_mock.add(User(friend.id, friend.username))

    # TODO: Tests
