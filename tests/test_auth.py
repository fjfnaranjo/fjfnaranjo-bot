from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from fjfnaranjobot.auth import (
    CFG_KEY,
    FriendMustBeIntError,
    add_friend,
    del_friend,
    ensure_int,
    get_friends,
    get_owner_id,
    logger,
    only_friends,
    only_owner,
    only_real,
)
from fjfnaranjobot.utils import EnvValueError

from .base import (
    FIRST_FRIEND_USERID,
    JSON_FIRST_FRIEND,
    JSON_NO_FRIENDS,
    JSON_ONE_FRIEND,
    JSON_SECOND_FRIEND,
    JSON_TWO_FRIENDS,
    OWNER_USERID,
    SECOND_FRIEND_USERID,
    UNKNOWN_USERID,
    BotTestCase,
)

MODULE_PATH = 'fjfnaranjobot.auth'


class AuthTests(BotTestCase):
    @contextmanager
    def _with_owner_and_friends(self, friends_list):
        with patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID):
            with patch(f'{MODULE_PATH}.get_key', return_value=friends_list):
                yield

    def test_get_owner_id_no_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', None, ['BOT_OWNER_ID']
        ):
            with self.assertRaises(EnvValueError) as e:
                get_owner_id()
            assert 'must be defined' in str(e.exception)

    def test_get_owner_id_env_not_int(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': 'a'}):
            with self.assertRaises(EnvValueError) as e:
                get_owner_id()
                assert 'Invalid id' in str(e)

    def test_get_owner_id_env(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': '1'}):
            assert get_owner_id() == 1

    def test_ensure_int_ok(self):
        ensured = ensure_int('53')
        assert ensured == 53
        assert isinstance(ensured, int)

    def test_ensure_int_empty(self):
        with self.assertRaises(FriendMustBeIntError):
            ensure_int('')

    def test_ensure_int_not_int(self):
        with self.assertRaises(FriendMustBeIntError):
            ensure_int('one')

    def test_only_any_logs_none_command(self):
        @only_real
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.message.text = 'cmd foo bar'
        update_mock.effective_user = None
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert 'Command text: \'cmd' in logs.output[0]

    def test_only_any_logs_command(self):
        @only_real
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.message = None
        update_mock.effective_user = None
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert 'Command text: \'unknown\'' in logs.output[0]

    def test_only_real_user_is_none(self):
        @only_real
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.effective_user = None
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert 'Message received with no user' in logs.output[0]

    def test_only_real_user_is_bot(self):
        @only_real
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.effective_user.is_bot = True
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert 'Bot with username' in logs.output[0]

    def test_only_real_user_ok(self):
        @only_real
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.effective_user.is_bot = False
        assert noop(update_mock) is True

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_ok(self, _get_owner_id):
        @only_owner
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.effective_user.id = OWNER_USERID
        update_mock.effective_user.is_bot = False
        assert noop(update_mock) is True

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_no_owner(self, _get_owner_id):
        @only_owner
        def noop(_update):
            return True

        update_mock = MagicMock()
        update_mock.effective_user.id = UNKNOWN_USERID
        update_mock.effective_user.is_bot = False
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert 'User ' in logs.output[0]
        assert 'tried to access a' in logs.output[0]

    def test_only_friends_is_friend(self):
        @only_friends
        def noop(_update):
            return True

        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            update_mock = MagicMock()
            update_mock.effective_user.id = FIRST_FRIEND_USERID
            update_mock.effective_user.is_bot = False
            assert noop(update_mock) is True

    def test_only_friends_not_friend(self):
        @only_friends
        def noop(_update):
            return True

        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            update_mock = MagicMock()
            update_mock.effective_user.id = UNKNOWN_USERID
            update_mock.effective_user.is_bot = False
            with self.assertLogs(logger) as logs:
                assert noop(update_mock) is None
            assert 'User ' in logs.output[0]
            assert 'tried to access a' in logs.output[0]

    def test_auth_get_friends_no_friends(self):
        with self._with_owner_and_friends(None):
            friends = get_friends()
            assert isinstance(friends, list)
            assert 0 == len(friends)

    def test_auth_get_friends_one_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            friends = get_friends()
            assert isinstance(friends, list)
            assert 1 == len(friends)
            assert FIRST_FRIEND_USERID in friends

    def test_auth_get_friends_many_friends(self):
        with self._with_owner_and_friends(JSON_TWO_FRIENDS):
            friends = get_friends()
            assert isinstance(friends, list)
            assert 2 == len(friends)
            assert FIRST_FRIEND_USERID in friends
            assert SECOND_FRIEND_USERID in friends

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
