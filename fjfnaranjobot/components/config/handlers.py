from telegram.ext import CommandHandler

from fjfnaranjobot.components.config.use_cases import config_get, config_set

group = 10

handlers = (
    CommandHandler('config_set', config_set),
    CommandHandler('config_get', config_get),
)
