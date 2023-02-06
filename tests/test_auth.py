from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch, sentinel

from telegram.ext import ApplicationHandlerStop

from fjfnaranjobot.auth import friends, logger, only_friends, only_owner, only_real
from fjfnaranjobot.common import SORRY_TEXT, User

from .base import (
    BOT_USER,
    FIRST_FRIEND_USER,
    OWNER_USER,
    SECOND_FRIEND_USER,
    UNKNOWN_USER,
    BotHandlerTestCase,
    BotTestCase,
)

MODULE_PATH = "fjfnaranjobot.auth"


class AuthTests(BotHandlerTestCase):
    @staticmethod
    async def _mocked_handler(_update, _context):
        return sentinel.handler_return

    async def test_only_real_no_user_no_message(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_none(remove_message=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            "Message received with no user "
            "trying to access a only_real command. "
            "Command text: '<unknown>' (cropped to 10 chars)."
        ) in logs.output[0]

    async def test_only_real_no_user_empty_command(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_none(remove_text=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            "Message received with no user "
            "trying to access a only_real command. "
            "Command text: '<empty>' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_real_no_user(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_none()
        self.set_string_command("cmd")
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            "Message received with no user "
            "trying to access a only_real command. "
            "Command text: 'cmd' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_real_bot_no_message(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_bot(remove_message=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"Bot with username {BOT_USER.username} and id {BOT_USER.id} "
            "tried to access a only_real command. "
            "Command text: '<unknown>' (cropped to 10 chars)."
        ) in logs.output[0]

    async def test_only_real_bot_empty_command(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_bot(remove_text=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"Bot with username {BOT_USER.username} and id {BOT_USER.id} "
            "tried to access a only_real command. "
            "Command text: '<empty>' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_real_bot(self):
        decorated_handler = only_real(self._mocked_handler)
        self.user_is_bot()
        self.set_string_command("cmd")
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"Bot with username {BOT_USER.username} and id {BOT_USER.id} "
            "tried to access a only_real command. "
            "Command text: 'cmd' (cropped to 10 chars)."
        ) in logs.output[0]

    async def test_only_real_user_ok(self):
        decorated_handler = only_real(self._mocked_handler)
        assert (
            await decorated_handler(*self.update_and_context) is sentinel.handler_return
        )
        self.assert_message_calls([])

    async def test_only_owner_no_message(self):
        decorated_handler = only_owner(self._mocked_handler)
        self.user_is_unknown(remove_message=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"User u with id {UNKNOWN_USER.id} "
            "tried to access a only_owner command. "
            "Command text: '<unknown>' (cropped to 10 chars)."
        ) in logs.output[0]

    async def test_only_owner_empty_command(self):
        decorated_handler = only_owner(self._mocked_handler)
        self.user_is_unknown(remove_text=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"User u with id {UNKNOWN_USER.id} "
            "tried to access a only_owner command. "
            "Command text: '<empty>' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_owner_no_owner(self):
        decorated_handler = only_owner(self._mocked_handler)
        self.set_string_command("cmd")
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                assert await decorated_handler(*self.update_and_context) is None
        assert (
            f"User u with id {UNKNOWN_USER.id} "
            "tried to access a only_owner command. "
            "Command text: 'cmd' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_owner_ok(self):
        decorated_handler = only_owner(self._mocked_handler)
        self.user_is_owner()
        assert (
            await decorated_handler(*self.update_and_context) is sentinel.handler_return
        )
        self.assert_message_calls([])

    async def test_only_friends_no_message(self):
        decorated_handler = only_friends(self._mocked_handler)
        self.user_is_unknown(remove_message=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"User u with id {UNKNOWN_USER.id} "
            "tried to access a only_friends command. "
            "Command text: '<unknown>' (cropped to 10 chars)."
        ) in logs.output[0]

    async def test_only_friends_empty_command(self):
        decorated_handler = only_friends(self._mocked_handler)
        self.user_is_unknown(remove_text=True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(ApplicationHandlerStop):
                await decorated_handler(*self.update_and_context)
        assert (
            f"User u with id {UNKNOWN_USER.id} "
            "tried to access a only_friends command. "
            "Command text: '<empty>' (cropped to 10 chars)."
        ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_friends_not_friend(self):
        decorated_handler = only_friends(self._mocked_handler)
        self.set_string_command("cmd")
        with self.set_friends([FIRST_FRIEND_USER]):
            with self.assertLogs(logger) as logs:
                with self.assertRaises(ApplicationHandlerStop):
                    await decorated_handler(*self.update_and_context)
            assert (
                f"User u with id {UNKNOWN_USER.id} "
                "tried to access a only_friends command. "
                "Command text: 'cmd' (cropped to 10 chars)."
            ) in logs.output[0]
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_friends_ok(self):
        decorated_handler = only_friends(self._mocked_handler)
        self.user_is_friend(FIRST_FRIEND_USER)
        with self.set_friends([FIRST_FRIEND_USER]):
            assert (
                await decorated_handler(*self.update_and_context)
                is sentinel.handler_return
            )
            self.assert_message_calls([])

    async def test_only_owner_not_defined_no_message(self):
        with self.mocked_environ("fjfnaranjobot.auth.environ", None, ["BOT_OWNER_ID"]):
            decorated_handler = only_owner(self._mocked_handler)
            self.user_is_owner(remove_message=True)
            with self.assertLogs(logger) as logs:
                with self.assertRaises(ApplicationHandlerStop):
                    assert await decorated_handler(*self.update_and_context) is None
            assert (
                f"User o with id {OWNER_USER.id} "
                "tried to access a only_owner command. "
                "Command text: '<unknown>' (cropped to 10 chars)."
            ) in logs.output[0]

    async def test_only_owner_not_defined_empty_command(self):
        with self.mocked_environ("fjfnaranjobot.auth.environ", None, ["BOT_OWNER_ID"]):
            decorated_handler = only_owner(self._mocked_handler)
            self.user_is_owner(remove_text=True)
            with self.assertLogs(logger) as logs:
                with self.assertRaises(ApplicationHandlerStop):
                    assert await decorated_handler(*self.update_and_context) is None
            assert (
                f"User o with id {OWNER_USER.id} "
                "tried to access a only_owner command. "
                "Command text: '<empty>' (cropped to 10 chars)."
            ) in logs.output[0]
            self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    async def test_only_owner_not_defined(self):
        with self.mocked_environ("fjfnaranjobot.auth.environ", None, ["BOT_OWNER_ID"]):
            decorated_handler = only_owner(self._mocked_handler)
            self.user_is_owner()
            self.set_string_command("cmd")
            with self.assertLogs(logger) as logs:
                with self.assertRaises(ApplicationHandlerStop):
                    assert await decorated_handler(*self.update_and_context) is None
            assert (
                f"User o with id {OWNER_USER.id} "
                "tried to access a only_owner command. "
                "Command text: 'cmd' (cropped to 10 chars)."
            ) in logs.output[0]
            self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)


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
            friends.add(User(FIRST_FRIEND_USER.id, "x"))
            assert 1 == len(friends)
            assert FIRST_FRIEND_USER in friends
            for friend in friends:
                assert "x" == friend.username

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
