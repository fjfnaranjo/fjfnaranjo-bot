from telegram.ext import CommandHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.components.config.use_cases import config_get, config_set

group = 10


@only_owner
def config_get_handler(*args, **kwargs):
    config_get(*args, **kwargs)


@only_owner
def config_set_handler(*args, **kwargs):
    config_set(*args, **kwargs)


handlers = (
    CommandHandler('config_set', config_set_handler),
    CommandHandler('config_get', config_get_handler),
)
