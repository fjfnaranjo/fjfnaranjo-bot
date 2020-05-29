from telegram.ext import CommandHandler, Handler, MessageHandler, StringCommandHandler


class FakeHandler(Handler):
    def check_update(self, _update):
        return


group = 99

handlers = (
    CommandHandler('cmdm51', lambda: None),
    CommandHandler('cmdm52', lambda: None),
    StringCommandHandler('cmdm53', lambda: None),
    MessageHandler(None, lambda: None),
    FakeHandler(lambda: None),
)
