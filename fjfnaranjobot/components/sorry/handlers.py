from telegram.ext import Filters, MessageHandler

from fjfnaranjobot.components.sorry.use_cases import sorry

group = 90


def sorry_handler(*args, **kwargs):
    sorry(*args, **kwargs)


handlers = (MessageHandler(Filters.text, sorry),)
