from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.common import get_bot_owner_name
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def start_handler(update, context):
    logger.info(f"Greeting a new user with id {update.effective_user.id}.")
    owner_name = get_bot_owner_name()
    context.bot.send_message(
        update.message.chat.id, f"Welcome. I'm {owner_name}'s bot. How can I help you?",
    )
    raise DispatcherHandlerStop()


handlers = (CommandHandler('start', start_handler),)
