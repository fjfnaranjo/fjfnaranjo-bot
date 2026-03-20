# TODO: Tests
from fjfnaranjobot.command import AnyHandlerMixin, Command
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Sorry(AnyHandlerMixin, Command):
    dispatcher_group = 65536
    allow_chats = True

    async def handle(self):
        logger.debug("Sending 'sorry' back to the user.")
        await self.reply(SORRY_TEXT)
