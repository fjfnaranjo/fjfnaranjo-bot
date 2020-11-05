from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.command import (
        BotCommand,
        MessageCommandHandlerMixin,
        GroupMessageCommandHandlerMixin,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Sorry(
        BotCommand,
        MessageCommandHandlerMixin,
        GroupMessageCommandHandlerMixin
):
    name = 'nsorry'

    def handle_command(self):
        logger.debug("Sending 'sorry' back to the user.")
        self.reply(SORRY_TEXT)
