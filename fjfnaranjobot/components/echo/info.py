from telegram.ext import Filters, MessageHandler

from fjfnaranjobot.components.echo.use_cases import echo
from fjfnaranjobot.logging import getLogger


logger = getLogger(__name__)


handlers = (MessageHandler(Filters.text, echo),)
