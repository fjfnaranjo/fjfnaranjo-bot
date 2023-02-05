from telegram import MessageEntity
from telegram.ext import ApplicationHandlerStop, MessageHandler
from telegram.ext.filters import TEXT, ChatType, Entity

from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


async def sorry_handler(update, _context):
    logger.info("Sending 'sorry' back to the user.")

    await update.message.reply_text(SORRY_TEXT)
    raise ApplicationHandlerStop()


async def sorry_group_handler(update, context):
    bot_mention = "@" + context.bot.username
    mentions = update.message.parse_entities(MessageEntity.MENTION)
    mentions_keys = list(mentions.keys())
    if (
        len(mentions_keys) == 1
        and mentions[mentions_keys[0]] == bot_mention
        and update.message.text.find(bot_mention) == 0
    ):
        update.message.text = update.message.text.replace(bot_mention, "").strip()
        return await sorry_handler(update, context)


handlers = (
    MessageHandler(ChatType.PRIVATE & TEXT, sorry_handler),
    MessageHandler(
        ChatType.GROUP & TEXT & Entity(MessageEntity.MENTION),
        sorry_group_handler,
    ),
)
