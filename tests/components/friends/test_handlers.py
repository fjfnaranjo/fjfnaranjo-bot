from unittest.mock import patch

from fjfnaranjobot.components.friends.handlers import friends_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.friends.handlers'


@patch(f'{MODULE_PATH}.friends')
class FriendsHandlersTests(BotHandlerTestCase):
    def test_friends_called(self, friends):
        self._user_is_owner()
        friends_handler(self._update)
        assert friends.called


# TODO: Test auth control
