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
BOT_USERID = 91

JSON_FIRST_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_SECOND_FRIEND = f'[{SECOND_FRIEND_USERID}]'
JSON_ONE_FRIEND = f'[{FIRST_FRIEND_USERID}]'
JSON_TWO_FRIENDS = f'[{FIRST_FRIEND_USERID},{SECOND_FRIEND_USERID}]'


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
        self._update = MagicMock()
        self._context = MagicMock()

    @property
    def update(self):
        return self._update

    @property
    def update_and_context(self):
        return self._update, self._context

    def set_string_command(self, cmd, cmd_args=None):
        self._update.message.text = cmd + (
            (' ' + (' '.join(cmd_args))) if cmd_args is not None else ''
        )
        self._context.args = cmd_args

    def _update_spec(self, no_message=None, empty_command=None):
        if no_message:
            self._update = MagicMock(spec=['effective_user'])
        elif empty_command:
            self._update = MagicMock()
            self._update.message = MagicMock(spec=['reply_text'])

    def user_is_none(self, no_message=None, empty_command=None):
        self._update_spec(no_message, empty_command)
        self._update.effective_user = None

    def user_is_bot(self, no_message=None, empty_command=None):
        self._update_spec(no_message, empty_command)
        self._update.effective_user.is_bot = True
        self._update.effective_user.username = 'bot'
        self._update.effective_user.id = BOT_USERID

    def user_is_unknown(self, no_message=None, empty_command=None):
        self._update_spec(no_message, empty_command)
        self._update.effective_user.is_bot = False
        self._update.effective_user.username = 'unknown'
        self._update.effective_user.id = UNKNOWN_USERID

    def user_is_friend(
        self, id_=FIRST_FRIEND_USERID, no_message=None, empty_command=None
    ):
        self._update_spec(no_message, empty_command)
        self._update.effective_user.is_bot = False
        self._update.effective_user.id = id_

    def user_is_owner(self, no_message=None, empty_command=None):
        self._update_spec(no_message, empty_command)
        self._update.effective_user.is_bot = False
        self._update.effective_user.id = OWNER_USERID


class BotHandlerTestCase(BotUpdateContextTestCase):
    def setUp(self, *args, **kwargs):
        BotUpdateContextTestCase.setUp(self, *args, **kwargs)

        self._message_reply_text = MagicMock()
        self._message_reply_text.message_id = 101
        self._message_reply_text.chat.id = 102
        self._update.message.reply_text.return_value = self._message_reply_text

        self.user_data = None
        self.args = None

    @property
    def message_reply_text(self):
        return self._message_reply_text

    @property
    def user_data(self):
        return self._context.user_data

    @user_data.setter
    def user_data(self, new_user_data):
        self._context.user_data = new_user_data

    def assert_reply(self, text):
        self._update.message.reply_text.assert_called_once_with(text)

    def assert_edit(self, text, chat_id, message_id):
        self._context.bot.edit_message_text.assert_called_once_with(
            text, chat_id, message_id
        )

    def assert_delete(self, chat_id, message_id):
        self._context.bot.delete_message.assert_called_once_with(chat_id, message_id)

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
