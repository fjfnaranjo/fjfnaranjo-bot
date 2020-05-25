from contextlib import contextmanager
from logging import INFO
from os import environ
from unittest import TestCase
from unittest.mock import MagicMock, patch

from telegram.ext import DispatcherHandlerStop

OWNER_USERID = 11
FIRST_FRIEND_USERID = 21
SECOND_FRIEND_USERID = 22
THIRD_FRIEND_USERID = 23
UNKNOWN_USERID = 31
# BOT_USERID = 91

JSON_FIRST_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_SECOND_FRIEND = f'[{SECOND_FRIEND_USERID}]'
JSON_ONE_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_TWO_FRIENDS = f'[{FIRST_FRIEND_USERID},{SECOND_FRIEND_USERID}]'


class BotTestCase(TestCase):
    @contextmanager
    def _with_mocked_environ(self, path, edit_keys=None, delete_keys=None):
        if edit_keys is None:
            edit_keys = {}
        if delete_keys is None:
            delete_keys = []
        if not hasattr(self, '_environ'):
            self._environ = environ.copy()
        for key in delete_keys:
            if key in self._environ:
                del self._environ[key]
        for key in edit_keys:
            self._environ[key] = edit_keys[key]
        with patch.dict(path, self._environ.copy(), True):
            yield


class BotHandlerTestCase(BotTestCase):
    def setUp(self):
        TestCase.setUp(self)
        self._update = MagicMock()
        self._context = MagicMock()

    def _set_string_command(self, cmd, cmd_args=None):
        self._update.message.text = f'{cmd} ' + (
            ' '.join(cmd_args) if cmd_args is not None else ''
        )
        self._context.args = cmd_args

    @contextmanager
    def _assert_reply_log_dispatch(self, reply, info, logger, level=INFO):
        with self.assertLogs(logger, level) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                yield
            self._update.message.reply_text.assert_called_once_with(reply)
        assert info in logs.output[-1]

    #     def _user_is_none(self):
    #         self._update.effective_user = None
    #
    #     def _user_is_bot(self):
    #         self._update.effective_user.is_bot = True
    #         self._update.effective_user.id = BOT_USERID
    #
    #     def _user_is_unknown(self):
    #         self._update.effective_user.is_bot = False
    #         self._update.effective_user.id = UNKNOWN_USERID
    #
    #     def _user_is_friend(self, id_=FIRST_FRIEND_USERID):
    #         self._update.effective_user.is_bot = False
    #         self._update.effective_user.id = id_

    def _user_is_owner(self):
        self._update.effective_user.is_bot = False
        self._update.effective_user.id = OWNER_USERID
