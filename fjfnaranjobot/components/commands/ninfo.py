from fjfnaranjobot.auth import n_only_owner
from fjfnaranjobot.bot import command_list
from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Commands(BotCommand, CommandHandlerMixin):
    name = "ncommands"
    description = "Print the list of bot commands."
    is_dev_command = True

    @n_only_owner
    def handle_command(self):
        logger.info("Sending list of commands.")

        prod_commands = [
            command.prod_command + " - " + command.description
            for command in command_list
            if command.prod_command is not None
        ]
        dev_commands = [
            command.dev_command + " - " + command.description
            for command in command_list
            if command.dev_command is not None
        ]
        self.reply(
            "\n".join(prod_commands) if len(prod_commands) > 1 else "no commands"
        )
        self.reply("\n".join(dev_commands) if len(dev_commands) > 1 else "no commands")
