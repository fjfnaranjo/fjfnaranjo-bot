from telegram import MessageEntity
from telegram.ext import DispatcherHandlerStop, Filters, MessageHandler

from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def sorry_handler(update, _context):
    logger.info("Sending 'sorry' back to the user.")

    update.message.reply_text(SORRY_TEXT)
    raise DispatcherHandlerStop()


def sorry_group_handler(update, context):
    bot_mention = '@' + context.bot.username
    mentions = update.message.parse_entities(MessageEntity.MENTION)
    mentions_keys = list(mentions.keys())
    if (
        len(mentions_keys) == 1
        and mentions[mentions_keys[0]] == bot_mention
        and update.message.text.find(bot_mention) == 0
    ):
        update.message.text = update.message.text.replace(bot_mention, '').strip()
        return sorry_handler(update, context)


handlers = (
    MessageHandler(Filters.private & Filters.text, sorry_handler),
    MessageHandler(
        Filters.group & Filters.text & Filters.entity(MessageEntity.MENTION),
        sorry_group_handler,
    ),
)
