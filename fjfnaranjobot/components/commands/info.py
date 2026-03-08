# TODO: Tests
from fjfnaranjobot.bot import command_list
from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Commands(CommandHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "commands"
    description = "Print the list of bot commands."
    is_dev_command = True

    async def handle(self):
        logger.debug("Sending list of commands.")

        dev_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_dev_command")
            and command.is_dev_command
            and command.command_name is not None
        ]
        await self.reply("Dev commands:")
        await self.reply(
            "\n".join(dev_commands) if len(dev_commands) > 1 else "no commands"
        )

        prod_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_prod_command")
            and command.is_prod_command
            and command.command_name is not None
        ]
        await self.reply("Production commands:")
        await self.reply(
            "\n".join(prod_commands) if len(prod_commands) > 1 else "no commands"
        )
