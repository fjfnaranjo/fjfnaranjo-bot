from fjfnaranjobot.command import AnyHandlerMixin, BotCommand
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Sorry(BotCommand, AnyHandlerMixin):
    dispatcher_group = 65536
    allow_chats = True

    async def entrypoint(self):
        logger.debug("Sending 'sorry' back to the user.")
        await self.reply(SORRY_TEXT)
