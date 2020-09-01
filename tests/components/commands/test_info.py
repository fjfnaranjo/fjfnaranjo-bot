from unittest.mock import patch, sentinel

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import SORRY_TEXT, Command
from fjfnaranjobot.components.commands.info import commands_handler, logger

from ...base import (
    LOG_BOT_UNAUTHORIZED_HEAD,
    LOG_FRIEND_UNAUTHORIZED_HEAD,
    LOG_NO_USER_HEAD,
    LOG_USER_UNAUTHORIZED_HEAD,
    BotHandlerTestCase,
    CallWithMarkup,
)

MODULE_PATH = 'fjfnaranjobot.components.commands.info'


class CommandsHandlersTests(BotHandlerTestCase):
    def test_commands_handler_user_is_none(self):
        self.user_is_none()
        with self.assert_log_dispatch(LOG_NO_USER_HEAD, auth_logger):
            commands_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_commands_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assert_log_dispatch(LOG_USER_UNAUTHORIZED_HEAD, auth_logger):
            commands_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_commands_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assert_log_dispatch(LOG_BOT_UNAUTHORIZED_HEAD, auth_logger):
            commands_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_commands_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assert_log_dispatch(LOG_FRIEND_UNAUTHORIZED_HEAD, auth_logger):
            commands_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    @patch(
        f'{MODULE_PATH}.command_list',
        [
            Command('a desc', 'a', None),
            Command('b desc', 'b', None),
            Command('c desc', None, 'c'),
            Command('d desc', None, 'd'),
        ],
    )
    def test_commands_handler(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_reply_calls(
            [
                CallWithMarkup("a - a desc\nb - b desc"),
                CallWithMarkup("c - c desc\nd - d desc"),
            ]
        )

    @patch(
        f'{MODULE_PATH}.command_list',
        [
            Command('a desc', 'a', None),
            Command('b desc', 'b', None),
        ],
    )
    def test_commands_handler_only_prod(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_reply_calls(
            [
                CallWithMarkup("a - a desc\nb - b desc"),
                CallWithMarkup("no commands"),
            ]
        )

    @patch(
        f'{MODULE_PATH}.command_list',
        [
            Command('c desc', None, 'c'),
            Command('d desc', None, 'd'),
        ],
    )
    def test_commands_handler_only_dev(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_reply_calls(
            [
                CallWithMarkup("no commands"),
                CallWithMarkup("c - c desc\nd - d desc"),
            ]
        )
