from fjfnaranjobot.bot import command_list
from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Commands(CommandHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "ncommands"
    description = "Print the list of bot commands."
    is_dev_command = True

    async def entrypoint(self):
        logger.debug("Sending list of commands.")

        # TODO: When old commands removed, remove double parser
        dev_commands = [
            command.dev_command + " - " + command.description
            for command in command_list
            if hasattr(command, "dev_command") and command.dev_command is not None
        ]
        await self.reply("Old style dev commands:")
        await self.reply(
            "\n".join(dev_commands) if len(dev_commands) > 1 else "no commands"
        )

        n_dev_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_dev_command")
            and command.is_dev_command
            and command.command_name is not None
        ]
        await self.reply("New style dev commands:")
        await self.reply(
            "\n".join(n_dev_commands) if len(n_dev_commands) > 1 else "no commands"
        )

        prod_commands = [
            command.prod_command + " - " + command.description
            for command in command_list
            if hasattr(command, "prod_command") and command.prod_command is not None
        ]
        await self.reply("Old style production commands:")
        await self.reply(
            "\n".join(prod_commands) if len(prod_commands) > 1 else "no commands"
        )

        n_prod_commands = [
            command.command_name + " - " + command.description
            for command in command_list
            if hasattr(command, "is_prod_command")
            and command.is_prod_command
            and command.command_name is not None
        ]
        await self.reply("New style production commands:")
        await self.reply(
            "\n".join(n_prod_commands) if len(n_prod_commands) > 1 else "no commands"
        )
