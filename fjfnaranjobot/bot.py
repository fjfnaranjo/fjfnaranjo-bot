from json import loads, JSONDecodeError

from telegram import Bot as TBot, Update
from telegram.ext import Dispatcher

from fjfnaranjobot import BOT_TOKEN, BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN


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
        pass

    def update_webhook(self):
        self.bot.set_webhook(
            url=self.webhook_url
        )

    def process_request(self, url_path, update):
        if url_path != '/' + BOT_WEBHOOK_TOKEN:
            raise BotTokenError("Not for me.")

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

    def start_webhook(self, host='0.0.0.0', port=8080):
        self.updater.start_webhook(
            listen=host,
            port=port,
            url_path=BOT_WEBHOOK_TOKEN,
            webhook_url=self.webhook_url
        )
