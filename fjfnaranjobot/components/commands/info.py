from telegram.ext import ApplicationHandlerStop, CommandHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import Command, command_list
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_owner
def commands_handler(update, _context):
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
    update.message.reply_text(
        "\n".join(prod_commands) if len(prod_commands) > 1 else "no commands",
    )
    update.message.reply_text(
        "\n".join(dev_commands) if len(dev_commands) > 1 else "no commands",
    )
    raise ApplicationHandlerStop()


handlers = (CommandHandler("commands", commands_handler),)

commands = (Command("Print the list of bot commands.", None, "commands"),)
