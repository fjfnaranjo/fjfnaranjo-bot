from telegram.ext import CommandHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.components.friends.use_cases import friends

group = 10


@only_owner
def friends_handler(*args, **kwargs):
    friends(*args, **kwargs)


handlers = (CommandHandler('friends', friends),)
