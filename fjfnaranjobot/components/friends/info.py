# TODO: Review all tests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from fjfnaranjobot.auth import friends, only_owner
from fjfnaranjobot.common import Command, User, inline_handler, quote_value_for_log
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

KEYBOARD_ROWS = 5

#
# friends_handler states
#
# cmd --> GET_ADD_OR_DEL --> LIST       --> LIST
#                                       --> DEL_FRIEND_CONFIRM --> end
#                                       --> end
#                        --> ADD_FRIEND --> end
#                        --> DEL_FRIEND --> end
#
# * --> end
#

GET_ADD_OR_DEL, LIST, DEL_FRIEND_CONFIRM, ADD_FRIEND, DEL_FRIEND = range(5)


def _clear_context_data(context):
    chat_data_known_keys = [
        'chat_id',
        'message_id',
        'offset',
        'delete_user',
        'keyboard_users',
    ]
    for key in chat_data_known_keys:
        if key in context.chat_data:
            del context.chat_data[key]


_cancel_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
)


@only_owner
def friends_handler(update, context):
    logger.info("Entering friends conversation.")

    keyboard = [
        [
            InlineKeyboardButton("List", callback_data='list'),
            InlineKeyboardButton("Add", callback_data='add'),
            InlineKeyboardButton("Delete", callback_data='del'),
        ],
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    reply = context.bot.send_message(
        update.message.chat.id,
        "You can list all your friends. "
        "Also, you can add or remove Telegram contacts and IDs to the list. "
        "You can also cancel the friends command at any time.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.chat_data['chat_id'] = reply.chat.id
    context.chat_data['message_id'] = reply.message_id
    return GET_ADD_OR_DEL


# TODO: Tests!
def list_handler(_update, context):
    offset = context.chat_data.get('offset', 0)
    logger.info(f"List of friends requested. Offset: {offset}.")

    if len(friends) == 0:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(context.chat_data['chat_id'], "You have no friends.")
        _clear_context_data(context)
        return ConversationHandler.END

    show_button = None
    keyboard = []
    keyboard_users = []
    if len(friends) <= KEYBOARD_ROWS:
        page_friends = friends.sorted()
    else:
        pending_friends = list(friends.sorted())[offset:]
        if len(pending_friends) < KEYBOARD_ROWS:
            show_button = 'restart'
            offset = 0
            page_friends = pending_friends
        else:
            show_button = 'next'
            offset += KEYBOARD_ROWS
            page_friends = pending_friends[:KEYBOARD_ROWS]

    for friend in enumerate(page_friends):
        keyboard.append(
            [InlineKeyboardButton(friend[1].username, callback_data=f'{friend[0]}')]
        )
        keyboard_users.append((friend[1].id, friend[1].username))

    if show_button == 'restart':
        keyboard.append([InlineKeyboardButton("Start again", callback_data='next')])
    elif show_button == 'next':
        keyboard.append([InlineKeyboardButton("Next page", callback_data='next')])

    keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
    friends_markup = InlineKeyboardMarkup(keyboard)
    context.chat_data['offset'] = offset
    context.chat_data['keyboard_users'] = keyboard_users

    context.bot.edit_message_text(
        "Your friends will be listed below in pages. "
        "You can request the next page (if apply) or "
        "select a friend if you want to remove it.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=friends_markup,
    )
    return LIST


def list_del_confirm_handler(update, context):
    query = update.callback_query.data
    logger.info(
        f"Received in-list friend deletion request for position {query}. "
        "Asking to confirm."
    )

    user_to_delete = User(*context.chat_data['keyboard_users'][int(query)])
    del context.chat_data['keyboard_users']
    context.chat_data['delete_user'] = (user_to_delete.id, user_to_delete.username)

    confirm_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Confirm", callback_data='confirm')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')],
        ]
    )
    context.bot.edit_message_text(
        f"Are you sure that you want to remove '{user_to_delete.username}' as a friend. ",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=confirm_markup,
    )
    return DEL_FRIEND_CONFIRM


def list_del_confirmed_handler(_update, context):
    logger.info("Received confirmation for deletion.")

    delete_user = User(*context.chat_data['delete_user'])
    del context.chat_data['delete_user']
    friends.discard(delete_user)

    context.bot.delete_message(
        context.chat_data['chat_id'], context.chat_data['message_id'],
    )
    context.bot.send_message(context.chat_data['chat_id'], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


def add_handler(_update, context):
    logger.info("Requesting contact to add as a friend.")

    context.bot.edit_message_text(
        "Send me the contact of the friend you want to add. Or its id.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return ADD_FRIEND


def add_friend_handler(update, context):
    contact = update.message.contact
    if contact.user_id is None:
        logger.info("Received a contact without a Telegram ID.")
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], "That doesn\'t look like a Telegram user.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    contact_first_name = getattr(contact, 'first_name', '')
    contact_last_name = getattr(contact, 'last_name', '')
    first_name = contact_first_name if contact_first_name is not None else ''
    last_name = contact_last_name if contact_last_name is not None else ''
    username = ' '.join([first_name, last_name]).strip()
    user = User(contact.user_id, username)

    logger.info(f"Received a contact. Adding {user.username} as a friend.")
    friends.add(user)
    context.bot.delete_message(
        context.chat_data['chat_id'], context.chat_data['message_id'],
    )
    context.bot.send_message(
        context.chat_data['chat_id'], f"Added {user.username} as a friend."
    )
    _clear_context_data(context)
    return ConversationHandler.END


def add_friend_id_handler(update, context):
    try:
        (user_id,) = update.message.text.split()
    except ValueError:

        shown_id = quote_value_for_log(update.message.text)
        logger.info(f"Received and invalid id {shown_id} trying to add a friend.")

        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], "That's not a contact nor a single valid id.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    else:
        try:
            user_id_int = int(user_id)
            if user_id_int < 0:
                raise ValueError()
        except ValueError:

            logger.info(
                f"Received and invalid number in id '{user_id}' trying to add a friend."
            )
            context.bot.delete_message(
                context.chat_data['chat_id'], context.chat_data['message_id'],
            )
            context.bot.send_message(
                context.chat_data['chat_id'], "That's not a contact nor a valid id.",
            )
            _clear_context_data(context)
            return ConversationHandler.END

        else:

            user = User(user_id_int, f"ID {user_id_int}")
            logger.info(f"Adding {user.username} as a friend.")

            friends.add(user)

            context.bot.delete_message(
                context.chat_data['chat_id'], context.chat_data['message_id'],
            )
            context.bot.send_message(
                context.chat_data['chat_id'], f"Added {user.username} as a friend."
            )
            _clear_context_data(context)
            return ConversationHandler.END


def del_handler(_update, context):
    logger.info("Requesting contact to remove as a friend.")

    context.bot.edit_message_text(
        "Send me the contact of the friend you want to remove. " "Or its id.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return DEL_FRIEND


def del_friend_handler(update, context):
    contact = update.message.contact

    if contact.user_id is None:
        logger.info("Received a contact without a Telegram ID.")
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], "That doesn\'t look like a Telegram user.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    contact_first_name = getattr(contact, 'first_name', '')
    contact_last_name = getattr(contact, 'last_name', '')
    first_name = contact_first_name if contact_first_name is not None else ''
    last_name = contact_last_name if contact_last_name is not None else ''
    username = ' '.join([first_name, last_name]).strip()
    user = User(contact.user_id, username)

    if user in friends:

        for friend in friends:
            if friend.id == user.id:
                friend_username = friend.username
        logger.info(f"Removing {friend_username} as a friend.")

        friends.discard(user)

        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], f"Removed {friend_username} as a friend."
        )
        _clear_context_data(context)
        return ConversationHandler.END

    else:

        logger.info(f"Not removing {user.username} because its not a friend.")

        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], f"{user.username} isn't a friend."
        )
        _clear_context_data(context)
        return ConversationHandler.END


def del_friend_id_handler(update, context):
    try:
        (user_id,) = update.message.text.split()
    except ValueError:

        shown_id = quote_value_for_log(update.message.text)
        logger.info(f"Received and invalid id {shown_id} trying to remove a friend.")

        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], "That's not a contact nor a single valid id.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    else:
        try:
            user_id_int = int(user_id)
            if user_id_int < 0:
                raise ValueError()
        except ValueError:

            logger.info(
                f"Received and invalid number in id '{user_id}' trying to remove a friend."
            )
            context.bot.delete_message(
                context.chat_data['chat_id'], context.chat_data['message_id'],
            )
            context.bot.send_message(
                context.chat_data['chat_id'], "That's not a contact nor a valid id.",
            )
            _clear_context_data(context)
            return ConversationHandler.END

        else:
            user = User(user_id_int, f"ID {user_id_int}")
            if user in friends:

                for friend in friends:
                    if friend.id == user.id:
                        friend_username = friend.username
                logger.info(f"Removing {friend_username} as a friend.")

                friends.discard(user)

                context.bot.delete_message(
                    context.chat_data['chat_id'], context.chat_data['message_id'],
                )
                context.bot.send_message(
                    context.chat_data['chat_id'],
                    f"Removed {friend_username} as a friend.",
                )
                _clear_context_data(context)
                return ConversationHandler.END

            else:
                logger.info(f"Not removing {user.username} because its not a friend.")

                context.bot.delete_message(
                    context.chat_data['chat_id'], context.chat_data['message_id'],
                )
                context.bot.send_message(
                    context.chat_data['chat_id'], f"{user.username} isn't a friend."
                )
                _clear_context_data(context)
                return ConversationHandler.END


def cancel_handler(_update, context):
    logger.info("Abort friends conversation.")

    if 'message_id' in context.chat_data:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
    context.bot.send_message(context.chat_data['chat_id'], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


cancel_inlines = {
    'cancel': cancel_handler,
}
action_inlines = {
    'list': list_handler,
    'add': add_handler,
    'del': del_handler,
    'cancel': cancel_handler,
}
list_pos_next_inlines = {
    '0': list_del_confirm_handler,
    '1': list_del_confirm_handler,
    '2': list_del_confirm_handler,
    '3': list_del_confirm_handler,
    '4': list_del_confirm_handler,
    'next': list_handler,
    'cancel': cancel_handler,
}
list_del_confirm_inlines = {
    'confirm': list_del_confirmed_handler,
    'cancel': cancel_handler,
}


handlers = (
    ConversationHandler(
        entry_points=[CommandHandler('friends', friends_handler)],
        states={
            GET_ADD_OR_DEL: [
                CallbackQueryHandler(inline_handler(action_inlines, logger)),
            ],
            LIST: [
                CallbackQueryHandler(inline_handler(list_pos_next_inlines, logger)),
            ],
            DEL_FRIEND_CONFIRM: [
                CallbackQueryHandler(inline_handler(list_del_confirm_inlines, logger)),
            ],
            ADD_FRIEND: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.contact, add_friend_handler),
                MessageHandler(Filters.text, add_friend_id_handler),
            ],
            DEL_FRIEND: [
                CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
                MessageHandler(Filters.contact, del_friend_handler),
                MessageHandler(Filters.text, del_friend_id_handler),
            ],
        },
        fallbacks=[],
    ),
)

commands = (Command("Manage friends.", None, 'friends',),)
