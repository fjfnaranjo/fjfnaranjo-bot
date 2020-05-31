from unittest.mock import patch

from fjfnaranjobot.components.commands.handlers import (
    commands_dev_handler,
    commands_handler,
    logger,
)

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.commands.handlers'


@patch(f'{MODULE_PATH}.command_list', ['a', 'b'])
@patch(f'{MODULE_PATH}.command_list_dev', ['c', 'd'])
class CommandsHandlersTests(BotHandlerTestCase):
    def test_commands_handler(self):
        with self.assert_log_dispatch('Sending list of commands.', logger):
            commands_handler(*self.update_and_context)
        self.assert_reply("a\nb")

    def test_commands_dev_handler(self):
        with self.assert_log_dispatch('Sending list of dev commands.', logger):
            commands_dev_handler(*self.update_and_context)
        self.assert_reply("c\nd")
