from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch

from fjfnaranjobot.auth import get_friends, CFG_KEY, add_friend, del_friend
from tests.base import (
    OWNER_USERID,
    JSON_ONE_FRIEND,
    JSON_TWO_FRIENDS,
    JSON_FIRST_FRIEND,
    JSON_SECOND_FRIEND,
    JSON_NO_FRIENDS,
    FIRST_FRIEND_USERID,
    SECOND_FRIEND_USERID,
)


MODULE_PATH = 'fjfnaranjobot.auth'


class AuthTests(TestCase):
    @contextmanager
    def _with_owner_and_friends(self, friends_list):
        with patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID):
            with patch(f'{MODULE_PATH}.get_key', return_value=friends_list):
                yield

    def test_auth_get_friends_no_friends(self):
        with self._with_owner_and_friends(None):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(0, len(friends))

    def test_auth_get_friends_one_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(1, len(friends))
            self.assertIn(FIRST_FRIEND_USERID, friends)

    def test_auth_get_friends_many_friends(self):
        with self._with_owner_and_friends(JSON_TWO_FRIENDS):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(2, len(friends))
            self.assertIn(FIRST_FRIEND_USERID, friends)
            self.assertIn(SECOND_FRIEND_USERID, friends)

    def test_auth_add_friend(self):
        with self._with_owner_and_friends(None):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                add_friend(FIRST_FRIEND_USERID)
                set_key.assert_called_once_with(CFG_KEY, JSON_FIRST_FRIEND)

    def test_auth_add_friend_already_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                add_friend(FIRST_FRIEND_USERID)
                set_key.assert_not_called()

    def test_auth_add_friend_is_owner(self):
        with self._with_owner_and_friends(None):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                add_friend(OWNER_USERID)
                set_key.assert_not_called()

    def test_auth_del_friend_not_friends(self):
        with self._with_owner_and_friends(None):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                del_friend(FIRST_FRIEND_USERID)
                set_key.assert_not_called()

    def test_auth_del_friend_not_a_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                del_friend(SECOND_FRIEND_USERID)
                set_key.assert_not_called()

    def test_auth_del_friend_one_friend(self):
        with self._with_owner_and_friends(JSON_TWO_FRIENDS):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                del_friend(FIRST_FRIEND_USERID)
                set_key.assert_called_once_with(CFG_KEY, JSON_SECOND_FRIEND)

    def test_auth_del_friend_last_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_key') as set_key:
                del_friend(FIRST_FRIEND_USERID)
                set_key.assert_called_once_with(CFG_KEY, JSON_NO_FRIENDS)
