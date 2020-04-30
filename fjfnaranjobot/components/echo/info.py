from logging import getLogger

from telegram.ext import Filters, MessageHandler

from fjfnaranjobot.components.echo.use_cases import echo


logger = getLogger(__name__)


handlers = (
    MessageHandler(Filters.text, echo),
)
