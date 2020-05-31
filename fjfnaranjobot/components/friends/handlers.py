from math import floor

from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import friends, only_owner
from fjfnaranjobot.common import User
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


PAGE_SIZE = 5


#
# cmd --> GET_ADD_OR_DEL --> GET_PAGE   --> GET_PAGE
#                                       --> ONLY_PAGE
#                        --> ADD_FRIEND --> end
#                        --> DEL_FRIEND --> end
#
# GET_ADD_OR_DEL, GET_PAGE, ONLY_PAGE, ADD_FRIEND, DEL_FRIEND --> end
#

GET_ADD_OR_DEL, GET_PAGE, ONLY_PAGE, ADD_FRIEND, DEL_FRIEND = range(5)


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
                raise ValueError()
        except ValueError:
            logger.info(f"Received an invalid page number '{context.args[0]}'.")
            context.bot.edit_message_text(
                f"The page '{context.args[0]}' is not a valid page number. "
                "Send the /friends_getpage command to request more pages (if aplicable)."
                "If you want to do something else, /friends_cancel .",
                *context.user_data['message_ids'],
            )
            return GET_PAGE
    else:
        page = context.user_data.get('page', 1) if context.user_data is not None else 1

    num_friends = len(friends)
    num_pages = floor(num_friends / PAGE_SIZE) + (
        1 if num_friends % PAGE_SIZE > 0 else 0
    )

    if page > num_pages:
        logger.info(
            f"Not sending the page {page} of friends because it doesn't exists."
        )
        context.bot.edit_message_text(
            f"The page {page} doesn't exists. "
            "Send the /friends_getpage command again to start from the first page."
            "If you want to do something else, /friends_cancel .",
            *context.user_data['message_ids'],
        )
        return GET_PAGE

    else:

        sorted_friends = list(friends.sorted())
        friends_page = "\n".join(
            [
                f"{friend.username}"
                for friend in sorted_friends[
                    (page - 1) * PAGE_SIZE : ((page - 1) * PAGE_SIZE) + PAGE_SIZE
                ]
            ]
        )

        if page == num_pages and num_pages > 1:
            logger.info(f"Sending the last page (page {page}) of friends.")
            context.bot.edit_message_text(
                f"This is the last page (page {page}) of your friends list. "
                "Send the /friends_getpage command again to start from the first page."
                "If you want to do something else, /friends_cancel ."
                f"\n\n{friends_page}",
                *context.user_data['message_ids'],
            )

        elif page == 1 and num_pages == 1:
            logger.info(f"Sending the only page of friends.")
            context.bot.edit_message_text(
                f"This is the only page of your friends list. "
                "If you want to do something else, /friends_cancel ."
                f"\n\n{friends_page}",
                *context.user_data['message_ids'],
            )
            return ONLY_PAGE
        elif page == 1:
            logger.info(f"Sending the first page of friends.")
            context.bot.edit_message_text(
                f"This is the first page of your friends list. "
                "Send the /friends_getpage command to request more pages."
                "If you want to do something else, /friends_cancel ."
                f"\n\n{friends_page}",
                *context.user_data['message_ids'],
            )
        else:
            logger.info(f"Sending the page {page} of friends.")
            context.bot.edit_message_text(
                f"This is the page {page} of your friends list. "
                "Send the /friends_getpage command to request more pages."
                "If you want to do something else, /friends_cancel ."
                f"\n\n{friends_page}",
                *context.user_data['message_ids'],
            )

    page += 1
    if page > num_pages:
        page = 1
    context.user_data['page'] = page

    return GET_PAGE


def add_handler(_update, context):
    logger.info("Requesting contact to add as a friend.")
    context.bot.edit_message_text(
        "Send me the contact of the friend you want to add. "
        "If you want to do something else, /friends_cancel .",
        *context.user_data['message_ids'],
    )
    return ADD_FRIEND


def add_friend_handler(update, context):
    contact = update.message.contact
    user = User(contact.user_id, ' '.join([contact.first_name, contact.last_name]))
    logger.info(f"Adding {user.username} as a friend.")
    friends.add(user)
    context.bot.delete_message(*context.user_data['message_ids'])
    del context.user_data['message_ids']
    update.message.reply_text(f"Added {user.username} as a friend.")
    return ConversationHandler.END


def del_handler(_update, context):
    logger.info("Requesting contact to remove as a friend.")
    context.bot.edit_message_text(
        "Send me the contact of the friend you want to remove. "
        "If you want to do something else, /friends_cancel .",
        *context.user_data['message_ids'],
    )
    return DEL_FRIEND


def del_friend_handler(update, context):
    contact = update.message.contact
    user = User(contact.user_id, ' '.join([contact.first_name, contact.last_name]))

    if user in friends:
        for friend in friends:
            if friend.id == user.id:
                friend_username = friend.username
        logger.info(f"Removing {friend_username} as a friend.")
        friends.discard(user)
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text(f"Removed {friend_username} as a friend.")
    else:
        logger.info(f"Not removing {user.username} because not a friend.")
        context.bot.delete_message(*context.user_data['message_ids'])
        del context.user_data['message_ids']
        update.message.reply_text(f"{user.username} isn't a friend.")

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
            ONLY_PAGE: [CommandHandler('config_cancel', cancel_handler),],
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

commands = ((None, 'friends',),)
