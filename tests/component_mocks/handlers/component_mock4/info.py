from telegram.ext import (
    BaseHandler,
    CommandHandler,
    MessageHandler,
    StringCommandHandler,
)


class FakeHandler(BaseHandler):
    check_update = lambda: None


handlers = (
    CommandHandler("cmdm41", lambda: None),
    CommandHandler("cmdm42", lambda: None),
    StringCommandHandler("cmdm43", lambda: None),
    MessageHandler(None, lambda: None),
    FakeHandler(lambda: None),
)
