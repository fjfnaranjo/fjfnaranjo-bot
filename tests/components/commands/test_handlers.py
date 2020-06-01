from unittest.mock import patch

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.components.commands.handlers import commands_handler, logger

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.commands.handlers'


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

    @patch(f'{MODULE_PATH}.command_list', [('a desc', 'a',), ('b desc', 'b',)])
    @patch(f'{MODULE_PATH}.command_list_dev', [('c desc', 'c',), ('d desc', 'd',)])
    def test_commands_handler(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["a - a desc\nb - b desc", "c - c desc\nd - d desc"])

    @patch(f'{MODULE_PATH}.command_list', [('a desc', 'a',), ('b desc', 'b',)])
    @patch(f'{MODULE_PATH}.command_list_dev', [])
    def test_commands_handler_only_prod(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["a - a desc\nb - b desc", "no commands"])

    @patch(f'{MODULE_PATH}.command_list', [])
    @patch(f'{MODULE_PATH}.command_list_dev', [('c desc', 'c',), ('d desc', 'd',)])
    def test_commands_handler_only_dev(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["no commands", "c - c desc\nd - d desc"])
