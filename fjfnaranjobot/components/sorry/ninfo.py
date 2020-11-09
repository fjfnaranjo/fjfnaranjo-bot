from fjfnaranjobot.command import AnyHandlerMixin, BotCommand
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Sorry(BotCommand, AnyHandlerMixin):
    group = 65536
    allow_groups = True

    def handle_command(self):
        logger.debug("Sending 'sorry' back to the user.")
        self.end(SORRY_TEXT)
