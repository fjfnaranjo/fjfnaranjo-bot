from telegram.ext import CommandHandler, Handler, MessageHandler, StringCommandHandler

handlers = (
    CommandHandler('cmdm41', lambda: None),
    CommandHandler('cmdm42', lambda: None),
    StringCommandHandler('cmdm43', lambda: None),
    MessageHandler(None, lambda: None),
    Handler(lambda: None),
)
