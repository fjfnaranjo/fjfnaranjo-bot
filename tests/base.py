from contextlib import contextmanager
from logging import INFO
from os import environ
from unittest import TestCase
from unittest.mock import MagicMock, patch

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.common import User

OWNER_USER = User(11, 'o')
FIRST_FRIEND_USER = User(21, 'f')
SECOND_FRIEND_USER = User(22, 's')
THIRD_FRIEND_USER = User(23, 't')
UNKNOWN_USER = User(31, 'u')
BOT_USER = User(41, 'b')


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


class BotUpdateContextTestCase(BotTestCase):
    def setUp(self, *args, **kwargs):
        BotTestCase.setUp(self, *args, **kwargs)
        self._update_mock = MagicMock()
        self.user_is_unknown()
        self._context_mock = MagicMock()

    @property
    def update(self):
        return self._update_mock

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


class BotHandlerTestCase(BotUpdateContextTestCase):
    def setUp(self, *args, **kwargs):
        BotUpdateContextTestCase.setUp(self, *args, **kwargs)

        self._message_reply_text_mock = MagicMock()
        self._message_reply_text_mock.message_id = 101
        self._message_reply_text_mock.chat.id = 102
        self._update_mock.message.reply_text.return_value = (
            self._message_reply_text_mock
        )

        self.user_data = None
        self.args = None

    def update_mock_spec(self, no_message=None, empty_command=None):
        if no_message or empty_command:
            raise NotImplementedError(
                "The arguments for methods of the user_is_* family destroy the "
                "mocked telegram.Update object inside the test case. "
                f"{self.__class__.__name__} use this mock to store state and to "
                "prevent malfunction the former functionality is disabled."
            )

    @property
    def message_reply_text(self):
        return self._message_reply_text_mock

    @property
    def user_data(self):
        return self._context_mock.user_data

    @user_data.setter
    def user_data(self, new_user_data):
        self._context_mock.user_data = new_user_data

    def assert_reply(self, text):
        self._update_mock.message.reply_text.assert_called_once_with(text)

    def assert_edit(self, text, chat_id, message_id):
        self._context_mock.bot.edit_message_text.assert_called_once_with(
            text, chat_id, message_id
        )

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
        with self.assertRaises(DispatcherHandlerStop):
            with self.assert_log(log_text, logger, min_log_level):
                yield
