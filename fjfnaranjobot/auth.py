from os import environ
from json import loads as from_json
from json import dumps as to_json

from fjfnaranjobot.config import get_key, set_key


BOT_OWNER_ID = int(environ.get('BOT_OWNER_ID'))
CFG_KEY = 'auth.friends'


def only_real(f):
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            return
        if user.is_bot:
            return
        return f(update, *args, **kwargs)

    return wrapper


def only_owner(f):
    @only_real
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            return
        if user.id != BOT_OWNER_ID:
            return
        return f(update, *args, **kwargs)

    return wrapper


def only_friends(f):
    @only_real
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            return
        friends = from_json(get_key(CFG_KEY))
        if user.id != BOT_OWNER_ID and friends is not None and user.id not in friends:
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
