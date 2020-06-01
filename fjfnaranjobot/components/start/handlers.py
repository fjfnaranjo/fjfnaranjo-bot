from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def start_handler(update, _context):
    logger.info(f"Greeting a new user with id {update.effective_user.id}.")
    update.message.reply_text("Welcome. I'm fjfnaranjo's bot. How can I help you?")
    raise DispatcherHandlerStop()


handlers = (CommandHandler('start', start_handler),)
