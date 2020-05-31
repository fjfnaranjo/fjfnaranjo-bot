from collections.abc import MutableSet
from contextlib import contextmanager
from functools import wraps
from os import environ

from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.common import SORRY_TEXT, User
from fjfnaranjobot.db import cursor
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


def get_owner_id():
    try:
        return int(environ['BOT_OWNER_ID'])
    except KeyError:
        raise ValueError("BOT_OWNER_ID var must be defined.")
    except (TypeError, ValueError):
        raise ValueError("Invalid id in BOT_OWNER_ID var.")


def _parse_command(update):
    message = getattr(update, 'message', None)
    if message is not None:
        return getattr(message, 'text', '<empty>')
    else:
        return '<unknown>'


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
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user is None:
            _report_no_user(update, 'only_real')
            if hasattr(update, 'message'):
                update.message.reply_text(SORRY_TEXT)
            raise DispatcherHandlerStop()
        if user.is_bot:
            _report_bot(update, user, 'only_real')
            if hasattr(update, 'message'):
                update.message.reply_text(SORRY_TEXT)
            raise DispatcherHandlerStop()
        return f(update, *args, **kwargs)

    return wrapper


def only_owner(f):
    @only_real
    @wraps(f)
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        if user.id != get_owner_id():
            _report_user(update, user, 'only_owner')
            if hasattr(update, 'message'):
                update.message.reply_text(SORRY_TEXT)
            raise DispatcherHandlerStop()
        return f(update, *args, **kwargs)

    return wrapper


class _FriendsProxy(MutableSet):
    @staticmethod
    @contextmanager
    def _friends_cursor():
        with cursor() as cur:
            cur.execute(
                'CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, username)'
            )
            yield cur

    def __contains__(self, user):
        with self._friends_cursor() as cur:
            cur.execute(
                'SELECT id FROM friends WHERE id=?', (user.id,),
            )
            exists = cur.fetchone()
            return True if exists is not None else None

    def __iter__(self, *, sort=False):
        statement = 'SELECT id, username FROM friends'
        if sort:
            statement += ' ORDER BY id'
        with self._friends_cursor() as cur:
            cur.execute(statement)
            rows = cur.fetchall()
        for row in rows:
            yield User(row[0], row[1])

    def __len__(self):
        with self._friends_cursor() as cur:
            cur.execute('SELECT count(*) FROM friends')
            return cur.fetchone()[0]

    def add(self, user):
        logger.debug(
            f"Adding user with id {user.id} and username {user.username} as a friend."
        )
        with self._friends_cursor() as cur:
            cur.execute(
                'SELECT id FROM friends WHERE id=?', (user.id,),
            )
            exists = True if len(cur.fetchall()) > 0 else False
            if exists:
                with self._friends_cursor() as cur:
                    cur.execute(
                        'UPDATE friends SET id=?, username=? WHERE id=?',
                        (user.id, user.username, user.id),
                    )
            else:
                with self._friends_cursor() as cur:
                    cur.execute(
                        'INSERT INTO friends VALUES (?, ?)', (user.id, user.username),
                    )

    def discard(self, user):
        logger.debug(
            f"Removing user with id {user.id} and username {user.username} as a friend."
        )
        with self._friends_cursor() as cur:
            cur.execute(
                'DELETE FROM friends WHERE id=?', (user.id,),
            )

    def sorted(self):
        return self.__iter__(sort=True)

    def __le__(self, _other):
        raise NotImplementedError


friends = _FriendsProxy()


def only_friends(f):
    @only_real
    @wraps(f)
    def wrapper(update, *args, **kwargs):
        user = update.effective_user
        friend = User(user.id, user.username)
        if user.id != get_owner_id() and friend not in friends:
            _report_user(update, user, 'only_friends')
            if hasattr(update, 'message'):
                update.message.reply_text(SORRY_TEXT)
            raise DispatcherHandlerStop()
        return f(update, *args, **kwargs)

    return wrapper
