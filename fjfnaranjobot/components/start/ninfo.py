from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
from fjfnaranjobot.common import get_bot_owner_name
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Start(CommandHandlerMixin, BotCommand):
    command_name = "nstart"
    description = "Starts the bot."

    async def entrypoint(self):
        logger.debug(f"Greeting a new user with id {self.update.effective_user.id}.")

        owner_name = get_bot_owner_name()
        await self.reply(f"Welcome. I'm {owner_name}'s bot. How can I help you?")
