from unittest.mock import patch

from telegram.ext.dispatcher import DispatcherHandlerStop

from fjfnaranjobot.components.friends.handlers import friends_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.friends.handlers'


@patch(f'{MODULE_PATH}.friends')
class FriendsHandlersTests(BotHandlerTestCase):
    def test_friends_called(self, friends):
        self._user_is_owner()
        self._set_msg('cmd arg1 arg2')
        with self.assertRaises(DispatcherHandlerStop):
            friends_handler(self._update, None)
        friends.assert_called_once_with(['cmd', 'arg1', 'arg2'])
