from unittest.mock import patch

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import Command
from fjfnaranjobot.components.commands.info import commands_handler, logger

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.commands.info'


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
        self.assert_replies(["a - a desc\nb - b desc", "c - c desc\nd - d desc"])

    @patch(
        f'{MODULE_PATH}.command_list',
        [Command('a desc', 'a', None), Command('b desc', 'b', None),],
    )
    def test_commands_handler_only_prod(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["a - a desc\nb - b desc", "no commands"])

    @patch(
        f'{MODULE_PATH}.command_list',
        [Command('c desc', None, 'c'), Command('d desc', None, 'd'),],
    )
    def test_commands_handler_only_dev(self):
        self.user_is_owner()
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_replies(["no commands", "c - c desc\nd - d desc"])
