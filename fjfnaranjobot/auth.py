from functools import wraps
from json import dumps as to_json
from json import loads as from_json
from os import environ

from fjfnaranjobot.config import config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

CFG_KEY = 'auth.friends'


def get_owner_id():
    try:
        return int(environ['BOT_OWNER_ID'])
    except KeyError:
        raise ValueError("BOT_OWNER_ID var must be defined.")
    except (TypeError, ValueError):
        raise ValueError("Invalid id in BOT_OWNER_ID var.")


def ensure_int(string):
    try:
        return int(string)
    except ValueError:
        raise ValueError("Error parsing id as int.")


def _parse_command(update):
    message = getattr(update, 'message')
    if message is not None:
        return getattr(message, 'text', '')
    else:
        return 'unknown'


def _report_no_user(update, permission):
    command = _parse_command(update)[:10]
    logger.info(
        "Message received with no user "
        f"trying to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def _report_bot(update, user, permission):
    command = _parse_command(update)[:10]
    logger.info(
        f"Bot with username {user.username} and id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def _report_user(update, user, permission):
    command = _parse_command(update)[:10]
    logger.info(
        f"User {user.username} with id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def only_real(f):
    @wraps(f)
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
    @wraps(f)
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user.id != get_owner_id():
            _report_user(update, user, 'only_owner')
            return
        return f(update, *args, **kwargs)

    return wrapper


def get_friends():
    try:
        friends = config[CFG_KEY]
    except KeyError:
        return []
    else:
        return [] if friends is None else [int(id_) for id_ in from_json(friends)]


def only_friends(f):
    @only_real
    @wraps(f)
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        friends = get_friends()
        if user.id != get_owner_id() and friends is not None and user.id not in friends:
            _report_user(update, user, 'only_friends')
            return
        return f(update, *args, **kwargs)

    return wrapper


def add_friend(id_):
    id_int = ensure_int(id_)
    friends = get_friends()
    if id_int not in friends and id_int != get_owner_id():
        friends.append(id_int)
        config[CFG_KEY] = to_json(friends)


def del_friend(id_):
    id_int = ensure_int(id_)
    friends = get_friends()
    if id_int in friends:
        friends.remove(id_int)
        if len(friends) == 0:
            del config[CFG_KEY]
        else:
            config[CFG_KEY] = to_json(friends)
