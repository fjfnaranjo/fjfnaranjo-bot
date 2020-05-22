from telegram.ext import CommandHandler

group = 99

handlers = [
    CommandHandler('cmd', lambda: None),
    CommandHandler('cmd2', lambda: None),
]
