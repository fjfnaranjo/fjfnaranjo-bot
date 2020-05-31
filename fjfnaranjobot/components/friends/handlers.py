from math import floor

from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import friends, only_owner
from fjfnaranjobot.common import User
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


PAGE_SIZE = 5


#
# cmd --> GET_ADD_OR_DEL --> GET_PAGE --> end
#                                ^-------
#                        --> ADD_FRIEND --> end
#                        --> DEL_FRIEND --> end
#
# GET_ADD_OR_DEL, GET_PAGE, ADD_FRIEND, DEL_FRIEND --> end
#

GET_ADD_OR_DEL, GET_PAGE, ADD_FRIEND, DEL_FRIEND = range(4)


@only_owner
def friends_handler(update, context):
    logger.info("Entering friends conversation.")
    reply = update.message.reply_text(
        "If you want to see your friends, use /friends_getpage . "
        "If you want to add a friend, /friends_add . "
        "If you want to remove a friend, /friends_del . "
        "If you want to do something else, /friends_cancel ."
    )
    context.user_data['message_ids'] = (reply.chat.id, reply.message_id)
    return GET_ADD_OR_DEL


def get_page_handler(_update, context):
    if len(context.args) == 1:
        try:
            page = int(context.args[0])
            if page < 1:
                raise ValueError("The page number must be a positive integer.")
        except ValueError:
            logger.info(f"Received an invalid page number '{context.args[0]}'.")
            context.bot.edit_message_text(
                f"The page '{context.args[0]}' is not a valid page number. "
                "Send the /friends_getpage command to request more pages (if aplicable)."
                "If you want to do something else, /friends_cancel .",
                *context.user_data['message_ids'],
            )
    else:
        page = context.user_data.get('page', 0)

    num_pages = floor(len(friends) / PAGE_SIZE)

    if page > num_pages:
        logger.info(f"Sending the page {page} of friends.")
        context.bot.edit_message_text(
            f"The page {page} doesn't exists. "
            "Send the /friends_getpage command again to start from the first page."
            "If you want to do something else, /friends_cancel .",
            *context.user_data['message_ids'],
        )

    elif page == num_pages:
        page_text = f"last page (page {page})"
        logger.info(f"Sending the {page_text} of friends.")
        context.bot.edit_message_text(
            f"This is the {page_text} of your friends list. "
            "Send the /friends_getpage command again to start from the first page."
            "If you want to do something else, /friends_cancel .",
            *context.user_data['message_ids'],
        )

    else:
        if page == 0:
            page_text = "first page"
        else:
            page_text = f"page {page}"
        logger.info(f"Sending the {page_text} of friends.")
        context.bot.edit_message_text(
            f"This is the {page_text} of your friends list. "
            "Send the /friends_getpage command to request more pages."
            "If you want to do something else, /friends_cancel .",
            *context.user_data['message_ids'],
        )

    page += 1
    if page > num_pages:
        page = 0
    context.user_data['page']

    return GET_PAGE


def add_handler(_update, context):
    logger.info("Requesting contact to add it as a friend.")
    context.bot.edit_message_text(
        "Send me the contact of the friend you want to add. "
        "If you want to do something else, /friends_cancel .",
        *context.user_data['message_ids'],
    )
    return ADD_FRIEND


def del_handler(_update, context):
    logger.info("Requesting contact to remove it as a friend.")
    context.bot.edit_message_text(
        "Send me the contact of the friend you want to remove. "
        "If you want to do something else, /friends_cancel .",
        *context.user_data['message_ids'],
    )
    return DEL_FRIEND


def add_friend_handler(update, _context):
    user = User(update.contact.user_id, '')
    username = ' '.join([update.contact.first_name, update.contact.last_name])

    if user not in friends:
        logger.info(f"Adding [{username}](tg://user?id={user.id}) as a friend.")
        friends.add(user)
        update.message.reply_text(
            f"Added [{username}](tg://user?id={user.id}) as a friend."
        )

    else:
        logger.info(
            f"Not adding [{username}](tg://user?id={user.id}) because already a friend."
        )
        update.message.reply_text(
            f"[{username}](tg://user?id={user.id}) is already a friend."
        )

    return ConversationHandler.END


def del_friend_handler(update, _context):
    user = User(update.contact.user_id, '')
    username = ' '.join([update.contact.first_name, update.contact.last_name])

    if user in friends:
        for friend in friends:
            friend_username = friend.username
        logger.info(
            f"Removing [{friend_username}](tg://user?id={user.id}) as a friend."
        )
        friends.discard(user)
        update.message.reply_text(
            f"Removed [{friend_username}](tg://user?id={user.id}) as a friend."
        )
    else:
        logger.info(
            f"Not removing [{username}](tg://user?id={user.id}) because not a friend."
        )
        update.message.reply_text(
            f"[{username}](tg://user?id={user.id}) isn't a friend."
        )

    return ConversationHandler.END


def cancel_handler(update, context):
    if 'message_ids' in context.user_data:
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
    if 'page' in context.user_data:
        del context.user_data['page']
    logger.info("Abort friends conversation.")
    update.message.reply_text("Ok.")
    return ConversationHandler.END


handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('friends', friends_handler)],
        states={
            GET_ADD_OR_DEL: [
                CommandHandler('friends_cancel', cancel_handler),
                CommandHandler('friends_getpage', get_page_handler),
                CommandHandler('friends_add', add_handler),
                CommandHandler('friends_del', del_handler),
            ],
            GET_PAGE: [
                CommandHandler('config_cancel', cancel_handler),
                CommandHandler('friends_getpage', get_page_handler),
            ],
            ADD_FRIEND: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.contact, add_friend_handler),
            ],
            DEL_FRIEND: [
                CommandHandler('config_cancel', cancel_handler),
                MessageHandler(Filters.contact, del_friend_handler),
            ],
        },
        fallbacks=[CommandHandler('friends_cancel', cancel_handler)],
    ),
)
