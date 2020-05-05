from telegram.ext import CommandHandler

from fjfnaranjobot.components.friends.use_cases import friends


group = 10

handlers = (CommandHandler('friends', friends),)
