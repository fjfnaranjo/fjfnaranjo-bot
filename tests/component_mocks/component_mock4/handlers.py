from telegram.ext import CommandHandler, Handler, MessageHandler, StringCommandHandler


class FakeHandler(Handler):
    def check_update(self, _update):
        return


handlers = (
    CommandHandler('cmdm41', lambda: None),
    CommandHandler('cmdm42', lambda: None),
    StringCommandHandler('cmdm43', lambda: None),
    MessageHandler(None, lambda: None),
    FakeHandler(lambda: None),
)
