from telegram.ext import CommandHandler, ConversationHandler

handlers = (
    ConversationHandler(
        entry_points=[
            CommandHandler('cmdm51', lambda: None),
        ],
        states={
            0: [
                CommandHandler('cmdm52', lambda: None),
            ],
        },
        fallbacks=[
            CommandHandler('cmdm53', lambda: None),
        ],
    ),
)
