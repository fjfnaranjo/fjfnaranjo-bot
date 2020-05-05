from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import (
    get_friends,
    add_friend,
    del_friend,
    only_owner,
    ensure_int,
)
from fjfnaranjobot.logging import getLogger


logger = getLogger(__name__)


def _friends_list(update):
    logger.info(f"Sending list of friends.")
    all_friends = get_friends()
    if len(all_friends) == 0:
        update.message.reply_text("You don't have any friend.")
    else:
        friend_list = ", ".join([str(id_) for id_ in all_friends])
        update.message.reply_text(f"Your friends are: {friend_list}")


def _friend_add(update, id_):
    logger.info(f"Adding @{id_} as a friend.")
    ensure_int(id_)
    add_friend(id_)
    update.message.reply_text(f"Added ${id_} as a friend.")


def _friend_del(update, id_):
    logger.info(f"Removing @{id_} as a friend.")
    ensure_int(id_)
    del_friend(id_)
    update.message.reply_text(f"Removed ${id_} as a friend.")


@only_owner
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
            update.message.reply_text(f"Uknown sub-command. Options are: add, del")
    else:
        update.message.reply_text(f"Invalid systax. Use: /friends [|add id|del id] .")
    raise DispatcherHandlerStop()
