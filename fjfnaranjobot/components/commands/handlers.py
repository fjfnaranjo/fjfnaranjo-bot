from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import command_list, command_list_dev
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_owner
def commands_handler(update, _context):
    logger.info("Sending list of commands.")
    prod_commands_text = "\n".join(
        command[1] + ' - ' + command[0] for command in command_list
    )
    dev_commands_text = "\n".join(
        command[1] + ' - ' + command[0] for command in command_list_dev
    )
    update.message.reply_text(
        prod_commands_text if prod_commands_text else 'no commands'
    )
    update.message.reply_text(dev_commands_text if dev_commands_text else 'no commands')
    raise DispatcherHandlerStop()


handlers = (CommandHandler('commands', commands_handler),)

commands = (("Print the list of bot commands.", None, 'commands'),)
