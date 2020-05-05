from os import environ
from json import loads as from_json
from json import dumps as to_json

from fjfnaranjobot.config import get_key, set_key
from fjfnaranjobot.logging import getLogger


logger = getLogger(__name__)

BOT_OWNER_ID = int(environ.get('BOT_OWNER_ID'))
CFG_KEY = 'auth.friends'


def _parse_command(update):
    message = getattr(update, 'message')
    if message is not None:
        return getattr(message, 'text', '')
    else:
        return 'unknown'


def _report_no_user(update, permission):
    command = _parse_command(update)[:10]
    logger.info(
        f"Message received with no user "
        f"trying to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars.)"
    )


def _report_bot(update, user, permission):
    command = _parse_command(update)[:10]
    logger.info(
        f"Bot with username {user.username} and id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars.)"
    )


def _report_user(update, user, permission):
    command = _parse_command(update)[:10]
    logger.info(
        f"User {user.username} with id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars.)"
    )


def only_real(f):
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            _report_no_user(update, 'only_real')
            return
        if user.is_bot:
            _report_bot(update, user, 'only_real')
            return
        return f(update, *args, **kwargs)

    return wrapper


def only_owner(f):
    @only_real
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            _report_no_user(update, 'only_owner')
            return
        if user.id != BOT_OWNER_ID:
            _report_user(update, user, 'only_owner')
            return
        return f(update, *args, **kwargs)

    return wrapper


def only_friends(f):
    @only_real
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            _report_no_user(update, 'only_friends')
            return
        friends = from_json(get_key(CFG_KEY))
        if user.id != BOT_OWNER_ID and friends is not None and user.id not in friends:
            _report_user(update, user, 'only_friends')
            return
        return f(update, *args, **kwargs)

    return wrapper


def get_friends():
    friends = get_key(CFG_KEY)
    return [] if friends is None else from_json(friends)


def add_friend(id_):
    friends = get_friends()
    if id_ not in friends and id_ != BOT_OWNER_ID:
        friends.append(id_)
        set_key(CFG_KEY, to_json(friends))


def del_friend(id_):
    friends = get_friends()
    if id_ in friends:
        friends.remove(id_)
        set_key(CFG_KEY, to_json(friends))
