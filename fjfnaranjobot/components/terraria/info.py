from telegram.ext import CommandHandler

from fjfnaranjobot.common import Command
from fjfnaranjobot.components.terraria.handlers.terraria import terraria_handler
from fjfnaranjobot.components.terraria.handlers.terraria_admin import (
    terraria_admin_conversation,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


handlers = (
    CommandHandler("terraria", terraria_handler),
    terraria_admin_conversation,
)

commands = (
    Command("Manage Terraria servers.", "terraria", "terraria"),
    Command("Manage Terraria servers (admin).", None, "terraria_admin"),
)
