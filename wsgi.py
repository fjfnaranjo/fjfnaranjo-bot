from os import environ

from telegram import Bot, Update as BotUpdate
from flask import Flask, request


application = Flask(__name__)
bot = Bot(token=environ.get('BOT_TOKEN'))


@application.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = BotUpdate.de_json(request.get_json(force=True), bot)

        chat_id = update.message.chat.id

        # Telegram understands UTF-8, so encode text for unicode compatibility
        text = update.message.text.encode('utf-8')

        # repeat the same message back (echo)
        bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'


@application.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{}/hook'.format(environ.get('BOT_URL')))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@application.route('/')
def index():
    return '.'
