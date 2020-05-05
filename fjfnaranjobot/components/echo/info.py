from telegram.ext import Filters, MessageHandler

from fjfnaranjobot.components.echo.use_cases import echo


group = 90

handlers = (MessageHandler(Filters.text, echo),)
