from fjfnaranjobot.command import AnyHandlerMixin, BotCommand
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Sorry(BotCommand, AnyHandlerMixin):
    group = 1

    def handle_command(self):
        logger.debug("Sending 'sorry' back to the user.")
        self.reply(SORRY_TEXT)
