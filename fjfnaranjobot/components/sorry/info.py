from telegram.ext import Filters, MessageHandler

from fjfnaranjobot.components.sorry.use_cases import sorry


group = 90

handlers = (MessageHandler(Filters.text, sorry),)
