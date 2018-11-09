from json import loads, JSONDecodeError

from telegram import Bot as TBot, Update
from telegram.ext import Dispatcher

from fjfnaranjobot import BOT_TOKEN, BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN
from fjfnaranjobot.component.echo import echo_handler
from fjfnaranjobot.component.config import config_set_handler, config_get_handler


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
        self.register_handlers()

    def register_handlers(self):
        self.dispatcher.add_handler(config_set_handler)
        self.dispatcher.add_handler(config_get_handler)
        self.dispatcher.add_handler(echo_handler)

    def process_request(self, url_path, update):

        # Root URL
        if url_path == '' or url_path == '/':
            return "I'm fjfnaranjo's bot."
    
        # Healt check URL
        elif url_path == '/ping':
            return 'pong'
    
        # Register webhook request URL
        elif url_path == (
            '/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook'))
        ):
            self.bot.set_webhook(
                url=self.webhook_url
            )
            return 'ok'

        # Register webhook request URL
        elif url_path == (
            '/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook_self'))
        ):
            self.bot.set_webhook(
                url=self.webhook_url,
                certificate=open('/botcert/YOURPUBLIC.pem', 'rb')
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
            self.dispatcher.process_update(
                Update.de_json(update_json, self.bot)
            )
        except Exception as e:
            raise BotLibraryError("Error in bot library.") from e

        return 'ok'

    def start_webhook(self, host='0.0.0.0', port=8080):
        self.updater.start_webhook(
            listen=host,
            port=port,
            url_path=BOT_WEBHOOK_TOKEN,
            webhook_url=self.webhook_url
        )
