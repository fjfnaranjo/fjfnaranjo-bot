from telegram.ext import CommandHandler, Handler, MessageHandler, StringCommandHandler

group = 99

handlers = (
    CommandHandler('cmdm51', lambda: None),
    CommandHandler('cmdm52', lambda: None),
    StringCommandHandler('cmdm53', lambda: None),
    MessageHandler(None, lambda: None),
    Handler(lambda: None),
)
