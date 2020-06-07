from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch

from telegram.ext.dispatcher import DispatcherHandlerStop

from fjfnaranjobot.auth import (
    friends,
    get_owner_id,
    logger,
    only_friends,
    only_owner,
    only_real,
)
from fjfnaranjobot.common import User
from tests.base import SECOND_FRIEND_USER, BotTestCase

from .base import (
    BOT_USER,
    FIRST_FRIEND_USER,
    OWNER_USER,
    UNKNOWN_USER,
    BotHandlerTestCase,
)

MODULE_PATH = 'fjfnaranjobot.auth'


class AuthGetEnvTests(BotTestCase):
    def test_get_owner_id_no_default(self):
        with self.mocked_environ(f'{MODULE_PATH}.environ', None, ['BOT_OWNER_ID']):
            with self.assertRaises(ValueError) as e:
                get_owner_id()
            assert 'BOT_OWNER_ID var must be defined.' == e.exception.args[0]

    def test_get_owner_id_env_not_int(self):
        with self.mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': 'a'}):
            with self.assertRaises(ValueError) as e:
                get_owner_id()
            assert 'Invalid id in BOT_OWNER_ID var.' == e.exception.args[0]

    def test_get_owner_id_env(self):
        with self.mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': '1'}):
            assert get_owner_id() == 1


class AuthTests(BotHandlerTestCase):
    @staticmethod
    @contextmanager
    def owner():
        with patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USER.id):
            yield

    @contextmanager
    def owner_and_friends(self, friend_list):
        with self.owner():
            friends.clear()
            for friend in friend_list:
                friends.add(User(friend.id, friend.username))
            yield
            friends.clear()

    def test_only_real_no_user_no_message(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_none(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_no_user_empty_command(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_none(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_no_user(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_none()
        self.set_string_command('cmd')
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot_no_message(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_bot(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'Bot with username {BOT_USER.username} and id {BOT_USER.id} '
            'tried to access a only_real command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot_empty_command(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_bot(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'Bot with username {BOT_USER.username} and id {BOT_USER.id} '
            'tried to access a only_real command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot(self):
        noop = only_real(lambda _update, _context: True)
        self.user_is_bot()
        self.set_string_command('cmd')
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'Bot with username {BOT_USER.username} and id {BOT_USER.id} '
            'tried to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_user_ok(self):
        noop = only_real(lambda _update, _context: True)
        assert noop(*self.update_and_context) is True

    def test_only_owner_no_message(self):
        noop = only_owner(lambda _update, _context: True)
        self.user_is_unknown(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'User u with id {UNKNOWN_USER.id} '
            'tried to access a only_owner command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_owner_empty_command(self):
        noop = only_owner(lambda _update, _context: True)
        self.user_is_unknown(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'User u with id {UNKNOWN_USER.id} '
            'tried to access a only_owner command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_owner_no_owner(self):
        noop = only_owner(lambda _update, _context: True)
        self.set_string_command('cmd')
        with self.owner():
            with self.assertLogs(logger) as logs:
                with self.assertRaises(DispatcherHandlerStop):
                    assert noop(*self.update_and_context) is None
        assert (
            f'User u with id {UNKNOWN_USER.id} '
            'tried to access a only_owner command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_owner_ok(self):
        with self.owner():
            noop = only_owner(lambda _update, _context: True)
            self.user_is_owner()
            assert noop(*self.update_and_context) is True

    def test_only_friends_no_message(self):
        noop = only_friends(lambda _update, _context: True)
        self.user_is_unknown(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'User u with id {UNKNOWN_USER.id} '
            'tried to access a only_friends command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_friends_empty_command(self):
        noop = only_friends(lambda _update, _context: True)
        self.user_is_unknown(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(*self.update_and_context)
        assert (
            f'User u with id {UNKNOWN_USER.id} '
            'tried to access a only_friends command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_friends_not_friend(self):
        noop = only_friends(lambda _update, _context: True)
        self.set_string_command('cmd')
        with self.owner_and_friends([FIRST_FRIEND_USER]):
            with self.assertLogs(logger) as logs:
                with self.assertRaises(DispatcherHandlerStop):
                    noop(*self.update_and_context)
            assert (
                f'User u with id {UNKNOWN_USER.id} '
                'tried to access a only_friends command. '
                'Command text: \'cmd\' (cropped to 10 chars).'
            ) in logs.output[0]

    def test_only_friends_ok(self):
        noop = only_friends(lambda _update, _context: True)
        self.user_is_friend(FIRST_FRIEND_USER)
        with self.owner_and_friends([FIRST_FRIEND_USER]):
            assert noop(*self.update_and_context) is True


class FriendsTests(TestCase):
    def setUp(self):
        super().setUp()
        friends.clear()

    @contextmanager
    def friends(self, friends_list):
        friends.clear()
        for friend in friends_list:
            friends.add(friend)
        yield
        friends.clear()

    def test_le_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            bool(friends <= 0)

    def test_no_friends(self):
        assert 0 == len(friends)

    def test_one_friend(self):
        with self.friends([FIRST_FRIEND_USER]):
            assert 1 == len(friends)
            assert FIRST_FRIEND_USER in friends

    def test_auth_get_friends_many_friends(self):
        with self.friends([FIRST_FRIEND_USER, SECOND_FRIEND_USER]):
            assert 2 == len(friends)
            assert FIRST_FRIEND_USER in friends
            assert SECOND_FRIEND_USER in friends

    def test_auth_get_friends_many_friends_sorted(self):
        with self.friends([SECOND_FRIEND_USER, FIRST_FRIEND_USER]):
            first_friend, second_friend = friends.sorted()
            assert FIRST_FRIEND_USER.id == first_friend.id
            assert SECOND_FRIEND_USER.id == second_friend.id

    def test_auth_add_friend(self):
        friends.add(FIRST_FRIEND_USER)
        assert 1 == len(friends)
        assert FIRST_FRIEND_USER in friends

    def test_auth_add_friend_already_friend(self):
        with self.friends([FIRST_FRIEND_USER]):
            friends.add(User(FIRST_FRIEND_USER.id, 'x'))
            assert 1 == len(friends)
            assert FIRST_FRIEND_USER in friends
            for friend in friends:
                assert 'x' == friend.username

    def test_auth_add_friend_is_owner(self):
        friends.add(OWNER_USER)
        assert 1 == len(friends)
        assert OWNER_USER in friends

    def test_auth_del_friend_not_friends(self):
        friends.discard(FIRST_FRIEND_USER)
        assert 0 == len(friends)

    def test_auth_del_friend_not_a_friend(self):
        with self.friends([FIRST_FRIEND_USER]):
            friends.discard(SECOND_FRIEND_USER)
            assert 1 == len(friends)
            assert FIRST_FRIEND_USER in friends

    def test_auth_del_friend_one_friend(self):
        with self.friends([FIRST_FRIEND_USER, SECOND_FRIEND_USER]):
            friends.discard(FIRST_FRIEND_USER)
            assert 1 == len(friends)
            assert SECOND_FRIEND_USER in friends

    def test_auth_del_friend_last_friend(self):
        with self.friends([FIRST_FRIEND_USER]):
            friends.discard(FIRST_FRIEND_USER)
            assert 0 == len(friends)
