from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.components.friends.use_cases import friends

group = 10


@only_owner
def friends_handler(update, _context):
    command_parts = update.message.text.split(' ')
    update.message.reply_text(friends(command_parts))
    raise DispatcherHandlerStop()


handlers = (CommandHandler('friends', friends),)
