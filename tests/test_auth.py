from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch

from fjfnaranjobot.auth import get_friends, CFG_KEY, add_friend, del_friend


class AuthTests(TestCase):
    @contextmanager
    def _with_owner_and_friends(self, owner_id, friends_list):
        with patch('fjfnaranjobot.auth.BOT_OWNER_ID', owner_id):
            with patch('fjfnaranjobot.auth.get_key', return_value=friends_list):
                yield

    def test_auth_get_friends_no_friends(self):
        with self._with_owner_and_friends(1, None):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(0, len(friends))

    def test_auth_get_friends_one_friend(self):
        with self._with_owner_and_friends(1, '[2]'):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(1, len(friends))
            self.assertIn(2, friends)

    def test_auth_get_friends_many_friends(self):
        with self._with_owner_and_friends(1, '[2, 3]'):
            friends = get_friends()
            self.assertIsInstance(friends, list)
            self.assertEqual(2, len(friends))
            self.assertIn(2, friends)
            self.assertIn(3, friends)

    def test_auth_add_friend(self):
        with self._with_owner_and_friends(1, None):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                add_friend(2)
                set_key.assert_called_once_with(CFG_KEY, '[2]')

    def test_auth_add_friend_already_friend(self):
        with self._with_owner_and_friends(1, '[2]'):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                add_friend(2)
                set_key.assert_not_called()

    def test_auth_add_friend_is_owner(self):
        with self._with_owner_and_friends(1, None):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                add_friend(1)
                set_key.assert_not_called()

    def test_auth_del_friend_not_friends(self):
        with self._with_owner_and_friends(1, None):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                del_friend(2)
                set_key.assert_not_called()

    def test_auth_del_friend_not_a_friend(self):
        with self._with_owner_and_friends(1, '[2]'):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                del_friend(3)
                set_key.assert_not_called()

    def test_auth_del_friend_one_friend(self):
        with self._with_owner_and_friends(1, '[2, 3]'):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                del_friend(2)
                set_key.assert_called_once_with(CFG_KEY, '[3]')

    def test_auth_del_friend_last_friend(self):
        with self._with_owner_and_friends(1, '[2]'):
            with patch('fjfnaranjobot.auth.set_key') as set_key:
                del_friend(2)
                set_key.assert_called_once_with(CFG_KEY, '[]')
