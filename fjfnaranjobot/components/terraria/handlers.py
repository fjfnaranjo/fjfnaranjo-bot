from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_owner
def terraria_handler(_update, _context):
    logger.info("The terraria command is not implemented.")
    raise DispatcherHandlerStop()


handlers = (CommandHandler('terraria', terraria_handler),)

commands = (("Manage Terraria servers.", 'terraria', 'terraria'),)
