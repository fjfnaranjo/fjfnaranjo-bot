from telegram.ext import CommandHandler, ConversationHandler

handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('cmdm71', lambda: None),],
        states={0: [CommandHandler('cmdm72', lambda: None),],},
        fallbacks=[CommandHandler('cmdm73', lambda: None),],
    ),
)
