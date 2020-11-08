from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
from fjfnaranjobot.common import get_bot_owner_name
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Start(BotCommand, CommandHandlerMixin):
    command_name = "nstart"

    def handle_command(self):
        logger.debug(f"Greeting a new user with id {self.update.effective_user.id}.")

        owner_name = get_bot_owner_name()
        self.reply(f"Welcome. I'm {owner_name}'s bot. How can I help you?")
