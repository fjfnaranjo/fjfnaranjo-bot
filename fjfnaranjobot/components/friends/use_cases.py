from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import add_friend, del_friend, ensure_int, get_friends
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def _friends_list(update):
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


def _friend_add(update, id_):
    id_int = ensure_int(id_)
    if id_int not in get_friends():
        logger.info(f"Adding @{id_int} as a friend.")
        add_friend(id_int)
        update.message.reply_text(f"Added @{id_int} as a friend.")
    else:
        logger.info(f"Not adding @{id_int} because already a friend.")
        update.message.reply_text(f"@{id_int} is already a friend.")


def _friend_del(update, id_):
    id_int = ensure_int(id_)
    if id_int in get_friends():
        logger.info(f"Removing @{id_int} as a friend.")
        del_friend(id_int)
        update.message.reply_text(f"Removed @{id_int} as a friend.")
    else:
        logger.info(f"Not removing @{id_int} because not a friend.")
        update.message.reply_text(f"@{id_int} isn't a friend.")


def friends(update, _context):
    command_parts = update.message.text.split(' ')
    if len(command_parts) == 1:
        _friends_list(update)
    elif len(command_parts) == 3:
        if command_parts[1] == 'add':
            _friend_add(update, command_parts[2])
        elif command_parts[1] == 'del':
            _friend_del(update, command_parts[2])
        else:
            logger.info("Invalid syntax for /friends command. Unknown sub-command.")
            update.message.reply_text(
                "Unknown sub-command. Options are: 'add' and 'del'."
            )
    else:
        logger.info("Invalid syntax for /friends command. Usage sent.")
        update.message.reply_text("Invalid syntax. Use: '/friends [|add id|del id]'.")
    raise DispatcherHandlerStop()
