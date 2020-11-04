from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.common import get_bot_owner_name
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def start_handler(update, _context):
    logger.info(f"Greeting a new user with id {update.effective_user.id}.")

    owner_name = get_bot_owner_name()
    update.message.reply_text(f"Welcome. I'm {owner_name}'s bot. How can I help you?")
    raise DispatcherHandlerStop()


handlers = (CommandHandler("start", start_handler),)
