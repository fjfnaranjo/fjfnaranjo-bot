from telegram.ext import Updater, StringCommandHandler

from fjfnaranjobot import BOT_TOKEN, BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN


class Bot:
    def __init__(self):
        self.updater = Updater(token=BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher
        self.register_handlers()
        update_webhook_handler = StringCommandHandler(
            'update_webhook',
            self.update_webhook,
        )
        self.dispatcher.add_handler(update_webhook_handler)

    def register_handlers(self):
        pass

    @staticmethod
    def update_webhook(bot, update):
        print('update_webhook')
        
    def start_webhook(self, host='0.0.0.0', port=8080):
        self.updater.start_webhook(
            listen=host,
            port=port,
            url_path=BOT_WEBHOOK_TOKEN,
            webhook_url='/'.join((BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN))
        )
