from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.common import command_list, command_list_dev
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def commands_handler(update, _context):
    logger.info("Sending list of commands.")
    update.message.reply_text("\n".join(command_list))
    raise DispatcherHandlerStop()


def commands_dev_handler(update, _context):
    logger.info("Sending list of dev commands.")
    update.message.reply_text("\n".join(command_list_dev))
    raise DispatcherHandlerStop()


handlers = (
    CommandHandler('commands', commands_handler),
    CommandHandler('commands_dev', commands_dev_handler),
)

commands = (
    ('commands', 'commands'),
    ('commands_dev', 'commands_dev'),
)
