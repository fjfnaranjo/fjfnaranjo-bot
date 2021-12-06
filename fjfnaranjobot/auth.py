# TODO: Clean _n
# TODO: Consider move only_ to commands mixins
from collections.abc import MutableSet
from functools import wraps
from os import environ

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.backends import sqldb
from fjfnaranjobot.common import SORRY_TEXT, User
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def get_owner_id():
    owner_id = environ.get("BOT_OWNER_ID")
    return int(owner_id) if owner_id is not None else None


def _reply_unauthorized(update, context):
    try:
        chat_id = update.message.chat.id
    except AttributeError:
        pass
    else:
        context.bot.send_message(chat_id, SORRY_TEXT)


def _parse_command(update):
    message = getattr(update, "message", None)
    if message is not None:
        return getattr(message, "text", "<empty>")
    else:
        return "<unknown>"


def _report_no_user(update, permission):
    command = _parse_command(update)[:10]
    logger.warning(
        "Message received with no user "
        f"trying to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def _report_bot(update, user, permission):
    command = _parse_command(update)[:10]
    logger.warning(
        f"Bot with username {user.username} and id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def _report_user(update, user, permission):
    command = _parse_command(update)[:10]
    logger.warning(
        f"User {user.username} with id {user.id} "
        f"tried to access a {permission} command. "
        f"Command text: '{command}' (cropped to 10 chars)."
    )


def only_real(f):
    @wraps(f)
    def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        if user is None:
            _reply_unauthorized(update, context)
            _report_no_user(update, "only_real")
            raise DispatcherHandlerStop()
        if user.is_bot:
            _reply_unauthorized(update, context)
            _report_bot(update, user, "only_real")
            raise DispatcherHandlerStop()
        return f(update, context, *args, **kwargs)

    return wrapper


def only_owner(f):
    @only_real
    @wraps(f)
    def wrapper(update, context, *args, **kwargs):
        owner_id = get_owner_id()
        user = update.effective_user
        if owner_id is None or user.id != owner_id:
            _reply_unauthorized(update, context)
            _report_user(update, user, "only_owner")
            raise DispatcherHandlerStop()
        return f(update, context, *args, **kwargs)

    return wrapper


# TODO: Use the micro orm here
class _FriendsProxy(MutableSet):
    def __init__(self):
        sqldb.execute(
            "CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, username)"
        )

    def __contains__(self, user):
        exists = sqldb.execute_and_fetch_one(
            "SELECT id FROM friends WHERE id=?",
            (user.id,),
        )
        return True if exists is not None else None

    def __iter__(self, *, sort=False):
        statement = "SELECT id, username FROM friends"
        if sort:
            statement += " ORDER BY id"
        rows = sqldb.execute_and_fetch_all(statement)
        for row in rows:
            yield User(row[0], row[1])

    def __len__(self):
        return sqldb.execute_and_fetch_one("SELECT count(*) FROM friends")[0]

    def add(self, user):
        logger.debug(
            f"Adding user with id {user.id} and username {user.username} as a friend."
        )
        current_friends = sqldb.execute_and_fetch_all(
            "SELECT id FROM friends WHERE id=?",
            (user.id,),
        )
        exists = True if len(current_friends) > 0 else False
        if exists:
            sqldb.execute(
                "UPDATE friends SET id=?, username=? WHERE id=?",
                (user.id, user.username, user.id),
            )
        else:
            sqldb.execute(
                "INSERT INTO friends VALUES (?, ?)",
                (user.id, user.username),
            )

    def discard(self, user):
        logger.debug(
            f"Removing user with id {user.id} and username {user.username} as a friend."
        )
        sqldb.execute(
            "DELETE FROM friends WHERE id=?",
            (user.id,),
        )

    def sorted(self):
        return self.__iter__(sort=True)

    def __le__(self, _other):
        raise NotImplementedError


friends = _FriendsProxy()


def only_friends(f):
    @only_real
    @wraps(f)
    def wrapper(update, context, *args, **kwargs):
        owner_id = get_owner_id()
        user = update.effective_user
        friend = User(user.id, user.username)
        if (owner_id is not None and user.id == owner_id) or friend not in friends:
            _reply_unauthorized(update, context)
            _report_user(update, user, "only_friends")
            raise DispatcherHandlerStop()
        return f(update, context, *args, **kwargs)

    return wrapper
