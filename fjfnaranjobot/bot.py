from importlib import import_module
from json import JSONDecodeError, loads
from os import environ

from telegram import Bot as TBot
from telegram import Update
from telegram.ext import Dispatcher


BOT_TOKEN = environ.get('BOT_TOKEN')
BOT_WEBHOOK_URL = environ.get('BOT_WEBHOOK_URL')
BOT_WEBHOOK_TOKEN = environ.get('BOT_WEBHOOK_TOKEN')
BOT_COMPONENTS = environ.get('BOT_COMPONENTS', 'config,echo')


class BotLibraryError(Exception):
    pass


class BotJSONError(Exception):
    pass


class BotTokenError(Exception):
    pass


class Bot:
    def __init__(self):
        self.bot = TBot(BOT_TOKEN)
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.webhook_url = '/'.join((BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN))
        for component in BOT_COMPONENTS.split(','):
            try:
                info = import_module('fjfnaranjobot.components.' f'{component}.info')
                try:
                    inits = info.inits
                except AttributeError:
                    pass
                else:
                    for init in inits:
                        init()
                try:
                    handlers = info.handlers
                except AttributeError:
                    pass
                else:
                    for handler in handlers:
                        self.dispatcher.add_handler(handler)
            except ModuleNotFoundError:
                pass

    def process_request(self, url_path, update):

        # Root URL
        if url_path == '' or url_path == '/':
            return "I'm fjfnaranjo's bot."

        # Healt check URL
        elif url_path == '/ping':
            return 'pong'

        # Register webhook request URL
        elif url_path == ('/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook'))):
            self.bot.set_webhook(url=self.webhook_url)
            return 'ok'

        # Register webhook request URL
        elif url_path == ('/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook_self'))):
            self.bot.set_webhook(
                url=self.webhook_url, certificate=open('/botcert/YOURPUBLIC.pem', 'rb')
            )
            return 'ok (self)'

        # Healt check URL
        elif url_path != '/' + BOT_WEBHOOK_TOKEN:
            raise BotTokenError()

        # Delegate response to bot library

        try:
            update_json = loads(update)
        except JSONDecodeError as e:
            raise BotJSONError("Sent content isn't JSON.") from e

        try:
            self.dispatcher.process_update(Update.de_json(update_json, self.bot))
        except Exception as e:
            raise BotLibraryError("Error in bot library.") from e

        return 'ok'

    def start_webhook(self, host='0.0.0.0', port=8080):
        self.updater.start_webhook(
            listen=host,
            port=port,
            url_path=BOT_WEBHOOK_TOKEN,
            webhook_url=self.webhook_url,
        )
