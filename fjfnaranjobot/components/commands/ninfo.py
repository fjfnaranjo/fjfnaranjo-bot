from fjfnaranjobot.bot import command_list
from fjfnaranjobot.command import ONLY_OWNER, BotCommand, CommandHandlerMixin
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Commands(BotCommand, CommandHandlerMixin):
    command_name = "ncommands"
    description = "Print the list of bot commands."
    is_dev_command = True
    permissions = ONLY_OWNER

    def handle_command(self):
        logger.debug("Sending list of commands.")

        # TODO: When old commands removed, remove double parser
        prod_commands = [
            command.prod_command + " - " + command.description
            for command in command_list
            if hasattr(command, "prod_command") and command.prod_command is not None
        ]
        prod_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_prod_command")
            and command.is_prod_command
            and command.command_name is not None
        ]
        dev_commands = [
            command.dev_command + " - " + command.description
            for command in command_list
            if hasattr(command, "dev_command") and command.dev_command is not None
        ]
        dev_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_dev_command")
            and command.is_dev_command
            and command.command_name is not None
        ]
        self.reply(
            "\n".join(prod_commands) if len(prod_commands) > 1 else "no commands"
        )
        self.reply("\n".join(dev_commands) if len(dev_commands) > 1 else "no commands")
