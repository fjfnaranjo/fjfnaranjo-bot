from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import command_list, command_list_dev
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_owner
def commands_handler(update, _context):
    logger.info("Sending list of commands.")
    update.message.reply_text("\n".join(command_list))
    update.message.reply_text("\n".join(command_list_dev))
    raise DispatcherHandlerStop()


handlers = (CommandHandler('commands', commands_handler),)

commands = ((None, 'commands'),)
