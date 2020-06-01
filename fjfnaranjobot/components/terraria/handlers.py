from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner, only_real
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


@only_real
def terraria_handler(_update, _context):
    logger.info("The terraria command is not implemented.")
    raise DispatcherHandlerStop()


@only_owner
def terraria_admin_handler(_update, _context):
    logger.info("The terraria admin command is not implemented.")
    raise DispatcherHandlerStop()


handlers = (
    CommandHandler('terraria', terraria_handler),
    CommandHandler('terraria_admin', terraria_admin_handler),
)

commands = (
    ("Manage Terraria servers.", 'terraria', 'terraria'),
    ("Manage Terraria servers (admin).", None, 'terraria_admin'),
)
