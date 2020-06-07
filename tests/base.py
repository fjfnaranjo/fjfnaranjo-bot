# Full test review: magic constants, reply/message/edit/delete mas call/callwithmk/params, default cancel inline
from contextlib import contextmanager
from logging import INFO
from os import environ
from unittest import TestCase
from unittest.mock import MagicMock, call, patch, sentinel

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.common import User

OWNER_USER = User(11, 'o')
FIRST_FRIEND_USER = User(21, 'f')
SECOND_FRIEND_USER = User(22, 's')
UNKNOWN_USER = User(31, 'u')
BOT_USER = User(41, 'b')

LOG_NO_USER_HEAD = 'Message received with no user'
LOG_USER_UNAUTHORIZED_HEAD = f'User {UNKNOWN_USER.username} with id {UNKNOWN_USER.id}'
LOG_BOT_UNAUTHORIZED_HEAD = (
    f'Bot with username {BOT_USER.username} and id {BOT_USER.id}'
)
LOG_FRIEND_UNAUTHORIZED_HEAD = (
    f'User {FIRST_FRIEND_USER.username} with id {FIRST_FRIEND_USER.id}'
)


class CallWithMarkup:
    def __init__(self, *args, reply_markup_dict=None, **kwargs):
        self.reply_markup_dict = reply_markup_dict
        self.call = call(*args, **kwargs)


class BotTestCase(TestCase):
    @contextmanager
    def mocked_environ(self, path, edit_keys=None, delete_keys=None):
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
        super().setUp()

        self._update_mock = MagicMock()
        self._update_mock.message.chat.id = sentinel.chat_id_from_update
        self._update_mock.message.message_id = sentinel.message_id_from_update

        self._context_mock = MagicMock()
        self._message_mock = MagicMock()
        self._message_mock.chat.id = sentinel.chat_id_from_send_message
        self._message_mock.message_id = sentinel.message_id_from_send_message
        self._context_mock.bot.send_message.return_value = self._message_mock
        self._context_mock.chat_data = None

        self.user_is_unknown()

    @property
    def update_and_context(self):
        return self._update_mock, self._context_mock

    def set_string_command(self, cmd, cmd_args=None):
        self._update_mock.message.text = cmd + (
            (' ' + (' '.join(cmd_args))) if cmd_args is not None else ''
        )
        self._context_mock.args = cmd_args

    def update_mock_spec(self, no_message=None, empty_command=None):
        if no_message:
            self._update_mock = MagicMock(spec=['effective_user'])
        elif empty_command:
            self._update_mock = MagicMock()
            self._update_mock.message = MagicMock(spec=['reply_text'])

    def user_is_none(self, no_message=None, empty_command=None):
        self.update_mock_spec(no_message, empty_command)
        self._update_mock.effective_user = None

    def user_is_bot(self, no_message=None, empty_command=None):
        self.update_mock_spec(no_message, empty_command)
        self._update_mock.effective_user.is_bot = True
        self._update_mock.effective_user.id = BOT_USER.id
        self._update_mock.effective_user.username = BOT_USER.username

    def user_is_unknown(self, no_message=None, empty_command=None):
        self.update_mock_spec(no_message, empty_command)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = UNKNOWN_USER.id
        self._update_mock.effective_user.username = UNKNOWN_USER.username

    def user_is_friend(
        self, friend=FIRST_FRIEND_USER, no_message=None, empty_command=None
    ):
        self.update_mock_spec(no_message, empty_command)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = friend.id
        self._update_mock.effective_user.username = friend.username

    def user_is_owner(self, no_message=None, empty_command=None):
        self.update_mock_spec(no_message, empty_command)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = OWNER_USER.id
        self._update_mock.effective_user.username = OWNER_USER.username

    @property
    def chat_data(self):
        return self._context_mock.chat_data

    @chat_data.setter
    def chat_data(self, new_chat_data):
        self._context_mock.chat_data = new_chat_data

    def _assert_messages(self, messages=tuple()):
        self.assertEqual(len(messages), self._context_mock.bot.send_message.call_count)
        for item in enumerate(messages):
            idx = item[0]
            call = item[1].call
            reply_markup_dict = item[1].reply_markup_dict
            called = self._context_mock.bot.send_message.mock_calls[idx]
            call_args = called[1]
            call_kwargs = called[2].copy()
            reply_markup_call = call_kwargs.get('reply_markup')
            if 'reply_markup' in call_kwargs:
                del call_kwargs['reply_markup']
            self.assertEqual(call, call(*call_args, **call_kwargs))
            if reply_markup_call is not None:
                self.assertEqual(reply_markup_dict, reply_markup_call.to_dict())

    def assert_message_calls(self, calls):
        self._assert_messages(calls)

    def assert_message_call(self, call):
        self._assert_messages([call])

    def assert_message_chat_text(self, chat_id, text):
        self._assert_messages([CallWithMarkup(chat_id, text)])

    def _assert_edit_text_chat_message(self, edits=tuple()):
        self.assertEqual(
            len(edits), self._context_mock.bot.edit_message_text.call_count
        )
        for item in enumerate(edits):
            idx = item[0]
            call = item[1].call
            reply_markup_dict = item[1].reply_markup_dict
            called = self._context_mock.bot.edit_message_text.mock_calls[idx]
            call_args = called[1]
            call_kwargs = called[2].copy()
            reply_markup_call = call_kwargs.get('reply_markup')
            if 'reply_markup' in call_kwargs:
                del call_kwargs['reply_markup']
            self.assertEqual(call, call(*call_args, **call_kwargs))
            if reply_markup_call is not None:
                self.assertEqual(reply_markup_dict, reply_markup_call.to_dict())

    def assert_edit_call(self, call):
        self._assert_edit_text_chat_message([call])

    def assert_delete(self, chat_id, message_id):
        self._context_mock.bot.delete_message.assert_called_once_with(
            chat_id, message_id
        )

    @contextmanager
    def assert_log(self, log_text, logger, min_log_level=INFO):
        with self.assertLogs(logger, min_log_level) as logs:
            yield
        self.assertIn(log_text, logs.output[-1])

    @contextmanager
    def assert_log_dispatch(self, log_text, logger, min_log_level=None):
        with self.assert_log(log_text, logger, min_log_level):
            with self.assertRaises(DispatcherHandlerStop):
                yield
