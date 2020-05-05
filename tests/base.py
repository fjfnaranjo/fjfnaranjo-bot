from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import MagicMock

from pytest import raises
from telegram.ext import DispatcherHandlerStop


OWNER_USERID = 11
FIRST_FRIEND_USERID = 21
SECOND_FRIEND_USERID = 22
THIRD_FRIEND_USERID = 23
UNKNOWN_USERID = 31
BOT_USERID = 91
JSON_FIRST_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_SECOND_FRIEND = f'[{SECOND_FRIEND_USERID}]'
JSON_THIRD_FRIEND = f'[{THIRD_FRIEND_USERID}]'
JSON_NO_FRIENDS = '[]'
JSON_ONE_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_TWO_FRIENDS = f'[{FIRST_FRIEND_USERID},{SECOND_FRIEND_USERID}]'
JSON_THREE_FRIENDS = (
    f'[{FIRST_FRIEND_USERID},{SECOND_FRIEND_USERID},{THIRD_FRIEND_USERID}]'
)


class BotUseCaseTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.update = MagicMock()

    def _user_is_none(self):
        self.update.effective_user = None

    def _user_is_bot(self):
        self.update.effective_user.is_bot = True
        self.update.effective_user.id = BOT_USERID

    def _user_is_unknown(self):
        self.update.effective_user.is_bot = False
        self.update.effective_user.id = UNKNOWN_USERID

    def _user_is_friend(self, id_=FIRST_FRIEND_USERID):
        self.update.effective_user.is_bot = False
        self.update.effective_user.id = id_

    def _user_is_owner(self):
        self.update.effective_user.is_bot = False
        self.update.effective_user.id = OWNER_USERID

    def _set_msg(self, msg):
        self.update.message.text = msg

    @contextmanager
    def _raises_dispatcher_stop(self):
        with raises(DispatcherHandlerStop):
            yield
