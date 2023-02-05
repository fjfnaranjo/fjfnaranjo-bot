from telegram.ext import ApplicationHandlerStop, CommandHandler

from fjfnaranjobot.common import get_bot_owner_name
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


async def start_handler(update, _context):
    logger.info(f"Greeting a new user with id {update.effective_user.id}.")

    owner_name = get_bot_owner_name()
    await update.message.reply_text(
        f"Welcome. I'm {owner_name}'s bot. How can I help you?"
    )
    raise ApplicationHandlerStop()


handlers = (CommandHandler("start", start_handler),)
