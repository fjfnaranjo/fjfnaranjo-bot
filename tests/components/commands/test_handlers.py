from unittest.mock import patch

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.components.commands.handlers import commands_handler, logger

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.commands.handlers'


@patch(f'{MODULE_PATH}.command_list', ['a', 'b'])
@patch(f'{MODULE_PATH}.command_list_dev', ['c', 'd'])
class CommandsHandlersTests(BotHandlerTestCase):
    def test_commands_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                commands_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_commands_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                commands_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_commands_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                commands_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_commands_handler(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["a\nb", "c\nd"])
