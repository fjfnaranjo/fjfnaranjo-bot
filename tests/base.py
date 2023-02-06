# Full test review: magic constants, reply/message/edit/delete mas call/callwithmk/params, default cancel inline
from contextlib import contextmanager
from logging import INFO
from os import environ
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, call, patch, sentinel

from telegram.ext import ApplicationHandlerStop

from fjfnaranjobot.auth import friends
from fjfnaranjobot.backends.sqldb.sqlite3 import SQLite3SQLDatabase
from fjfnaranjobot.common import User

BOT_USERNAME = "bu"

OWNER_USER = User(11, "o")
FIRST_FRIEND_USER = User(21, "f")
SECOND_FRIEND_USER = User(22, "s")
UNKNOWN_USER = User(31, "u")
BOT_USER = User(41, "b")

LOG_NO_USER_HEAD = "Message received with no user"
LOG_USER_UNAUTHORIZED_HEAD = f"User {UNKNOWN_USER.username} with id {UNKNOWN_USER.id}"
LOG_BOT_UNAUTHORIZED_HEAD = (
    f"Bot with username {BOT_USER.username} and id {BOT_USER.id}"
)
LOG_FRIEND_UNAUTHORIZED_HEAD = (
    f"User {FIRST_FRIEND_USER.username} with id {FIRST_FRIEND_USER.id}"
)


class CallWithMarkup:
    def __init__(self, *args, reply_markup_dict=None, **kwargs):
        self.reply_markup_dict = reply_markup_dict
        self.call = call(*args, **kwargs)


class MockedEnvironTestCase(TestCase):
    @contextmanager
    def mocked_environ(self, path, edit_keys=None, delete_keys=None):
        if edit_keys is None:
            edit_keys = {}
        if delete_keys is None:
            delete_keys = []
        if not hasattr(self, "_environ"):
            self._environ = environ.copy()
        for key in delete_keys:
            if key in self._environ:
                del self._environ[key]
        for key in edit_keys:
            self._environ[key] = edit_keys[key]
        with patch.dict(path, self._environ.copy(), True):
            yield


class MemoryDbTestCase(TestCase):
    def patch_sqldb(self, path):
        sqldb = SQLite3SQLDatabase(":memory:")
        sqldb_patcher = patch(path, sqldb)
        sqldb_patcher.start()
        self.addCleanup(sqldb_patcher.stop)
        return sqldb


class BotHandlerTestCase(MockedEnvironTestCase, IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()

        self._update_mock = MagicMock()
        self._message_from_update_mock = MagicMock()
        self._message_from_update_mock.chat.id = sentinel.chat_id_from_update
        self._message_from_update_mock.message_id = sentinel.message_id_from_update
        self._message_from_update_reply_text_mock = MagicMock()
        self._message_from_update_reply_text_mock.chat.id = sentinel.chat_id_from_update
        self._message_from_update_reply_text_mock.message_id = (
            sentinel.message_id_from_reply_text
        )
        self._update_mock.message = self._message_from_update_mock

        self._context_mock = MagicMock()
        self._context_mock.bot.username = BOT_USERNAME
        self._message_from_context_mock = MagicMock()
        self._message_from_context_mock.chat.id = sentinel.chat_id_from_send_message
        self._message_from_context_mock.message_id = (
            sentinel.message_id_from_send_message
        )
        self._context_mock.chat_data = None

        self._message_from_update_mock.reply_text = AsyncMock(
            return_value=self._message_from_update_reply_text_mock
        )
        self._context_mock.bot.delete_message = AsyncMock()
        self._context_mock.bot.edit_message_text = AsyncMock()
        self._context_mock.bot.send_message = AsyncMock(
            return_value=self._message_from_update_mock
        )

        self.user_is_unknown()

    @property
    def update_and_context(self):
        return self._update_mock, self._context_mock

    def set_string_command(self, cmd, cmd_args=None):
        self._update_mock.message.text = cmd + (
            (" " + (" ".join(cmd_args))) if cmd_args is not None else ""
        )
        self._context_mock.args = cmd_args

    def set_entities(self, entities):
        self._update_mock.message.parse_entities.return_value = entities

    def update_mock_spec(self, remove_message=None, remove_text=None):
        if remove_message:
            del self._update_mock.message
        elif remove_text:
            del self._update_mock.message.text

    @contextmanager
    def run(self, *args, **kwargs):
        with self.mocked_environ(
            "fjfnaranjobot.auth.environ", {"BOT_OWNER_ID": str(OWNER_USER.id)}
        ):
            return super().run(*args, **kwargs)

    @staticmethod
    @contextmanager
    def set_friends(friend_list):
        friends.clear()
        for friend in friend_list:
            friends.add(User(friend.id, friend.username))
        yield
        friends.clear()

    def user_is_none(self, remove_message=None, remove_text=None):
        self.update_mock_spec(remove_message, remove_text)
        self._update_mock.effective_user = None

    def user_is_bot(self, remove_message=None, remove_text=None):
        self.update_mock_spec(remove_message, remove_text)
        self._update_mock.effective_user.is_bot = True
        self._update_mock.effective_user.id = BOT_USER.id
        self._update_mock.effective_user.username = BOT_USER.username

    def user_is_unknown(self, remove_message=None, remove_text=None):
        self.update_mock_spec(remove_message, remove_text)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = UNKNOWN_USER.id
        self._update_mock.effective_user.username = UNKNOWN_USER.username

    def user_is_friend(
        self, friend=FIRST_FRIEND_USER, remove_message=None, remove_text=None
    ):
        self.update_mock_spec(remove_message, remove_text)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = friend.id
        self._update_mock.effective_user.username = friend.username

    def user_is_owner(self, remove_message=None, remove_text=None):
        self.update_mock_spec(remove_message, remove_text)
        self._update_mock.effective_user.is_bot = False
        self._update_mock.effective_user.id = OWNER_USER.id
        self._update_mock.effective_user.username = OWNER_USER.username

    @property
    def chat_data(self):
        return self._context_mock.chat_data

    @chat_data.setter
    def chat_data(self, new_chat_data):
        self._context_mock.chat_data = new_chat_data

    def _assert_reply(self, replies=tuple()):
        self.assertEqual(len(replies), self._update_mock.message.reply_text.call_count)
        for item in enumerate(replies):
            idx = item[0]
            call = item[1].call
            reply_markup_dict = item[1].reply_markup_dict
            called = self._update_mock.message.reply_text.mock_calls[idx]
            call_args = called[1]
            call_kwargs = called[2].copy()
            reply_markup_call = call_kwargs.get("reply_markup")
            if "reply_markup" in call_kwargs:
                del call_kwargs["reply_markup"]
            self.assertEqual(call, call(*call_args, **call_kwargs))
            if reply_markup_call is not None:
                self.assertEqual(reply_markup_dict, reply_markup_call.to_dict())

    def assert_reply_calls(self, calls):
        self._assert_reply(calls)

    def assert_reply_call(self, call):
        self._assert_reply([call])

    def assert_reply_text(self, text):
        self._assert_reply([CallWithMarkup(text)])

    def _assert_messages(self, messages=tuple()):
        self.assertEqual(len(messages), self._context_mock.bot.send_message.call_count)
        for item in enumerate(messages):
            idx = item[0]
            call = item[1].call
            # reply_markup_dict = item[1].reply_markup_dict
            called = self._context_mock.bot.send_message.mock_calls[idx]
            call_args = called[1]
            call_kwargs = called[2].copy()
            # reply_markup_call = call_kwargs.get('reply_markup')
            # if 'reply_markup' in call_kwargs:
            #    del call_kwargs['reply_markup']
            self.assertEqual(call, call(*call_args, **call_kwargs))
            # if reply_markup_call is not None:
            #    self.assertEqual(reply_markup_dict, reply_markup_call.to_dict())

    def assert_message_calls(self, calls):
        self._assert_messages(calls)

    # def assert_message_call(self, call):
    #    self._assert_messages([call])

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
            reply_markup_call = call_kwargs.get("reply_markup")
            if "reply_markup" in call_kwargs:
                del call_kwargs["reply_markup"]
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
            with self.assertRaises(ApplicationHandlerStop):
                yield
