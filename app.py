import logging

from fjfnaranjobot.bot import Bot


logging.basicConfig(level=logging.INFO)

bot = Bot()
bot.start_webhook()
