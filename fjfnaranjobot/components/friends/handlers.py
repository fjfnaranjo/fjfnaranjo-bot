from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import (
    add_friend,
    del_friend,
    ensure_int,
    get_friends,
    only_owner,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

group = 10


@only_owner
def friends_get_handler(update, _context):
    all_friends = get_friends()

    if len(all_friends) == 0:
        logger.info("Sending no friends.")
        update.message.reply_text("You don't have any friends.")
    elif len(all_friends) == 1:
        logger.info("Sending one friend.")
        the_friend = all_friends[0]
        update.message.reply_text(f"You only have one friend: '{the_friend}'.")
    elif len(all_friends) == 2:
        logger.info("Sending two friends.")
        first_friend, second_friend = all_friends
        update.message.reply_text(
            f"You have two friends: '{first_friend}' and '{second_friend}'."
        )

    else:
        logger.info("Sending list of friends.")
        last_friend = '\'' + str(all_friends[-1]) + '\''
        other_friends = all_friends[:-1]
        friend_list = ', '.join(['\'' + str(id_) + '\'' for id_ in other_friends])
        update.message.reply_text(f"Your friends are: {friend_list} and {last_friend}.")

    raise DispatcherHandlerStop()


@only_owner
def friends_add_handler(update, _context):
    _, id_ = update.message.text.split(' ')
    id_int = ensure_int(id_)

    if id_int not in get_friends():
        logger.info(f"Adding @{id_int} as a friend.")
        add_friend(id_int)
        update.message.reply_text(f"Added @{id_int} as a friend.")

    else:
        logger.info(f"Not adding @{id_int} because already a friend.")
        update.message.reply_text(f"@{id_int} is already a friend.")

    raise DispatcherHandlerStop()


@only_owner
def friends_del_handler(update, _context):
    _, id_ = update.message.text.split(' ')
    id_int = ensure_int(id_)

    if id_int in get_friends():
        logger.info(f"Removing @{id_int} as a friend.")
        del_friend(id_int)
        update.message.reply_text(f"Removed @{id_int} as a friend.")
    else:
        logger.info(f"Not removing @{id_int} because not a friend.")
        update.message.reply_text(f"@{id_int} isn't a friend.")

    raise DispatcherHandlerStop()


handlers = (CommandHandler('friends_get', friends_get_handler),)
handlers = (CommandHandler('friends_add', friends_add_handler),)
handlers = (CommandHandler('friends_del', friends_del_handler),)
