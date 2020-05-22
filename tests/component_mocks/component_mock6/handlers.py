from telegram.ext import CommandHandler

group = 'a'

handlers = [
    CommandHandler('cmd', lambda: None),
    CommandHandler('cmd2', lambda: None),
]
