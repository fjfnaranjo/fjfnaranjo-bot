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
from fjfnaranjobot.bot import EnvValueError

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
            with patch(f'{MODULE_PATH}.get_config', return_value=friends_list):
                yield

    def test_get_owner_id_no_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', None, ['BOT_OWNER_ID']
        ):
            with self.assertRaises(EnvValueError) as e:
                get_owner_id()
            assert 'BOT_OWNER_ID var must be defined.' in str(e.exception)

    def test_get_owner_id_env_not_int(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': 'a'}):
            with self.assertRaises(EnvValueError) as e:
                get_owner_id()
            assert 'Invalid id in BOT_OWNER_ID var.' in str(e.exception)

    def test_get_owner_id_env(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': '1'}):
            assert get_owner_id() == 1

    def test_ensure_int_ok(self):
        ensured = ensure_int('53')
        assert ensured == 53
        assert isinstance(ensured, int)

    def test_ensure_int_empty(self):
        with self.assertRaises(FriendMustBeIntError) as e:
            ensure_int('')
        assert 'Error parsing id as int.' in str(e.exception)

    def test_ensure_int_not_int(self):
        with self.assertRaises(FriendMustBeIntError):
            ensure_int('one')

    def test_only_all_logs_none_command(self):
        all_auth_filters = (only_real, only_owner, only_friends)
        for auth_filter in all_auth_filters:
            with self.subTest(auth_filter=auth_filter):
                noop = auth_filter(lambda _update: True)
                update_mock = MagicMock()
                update_mock.message.text = 'cmd foo bar'
                update_mock.effective_user = None
                with self.assertLogs(logger) as logs:
                    assert noop(update_mock) is None
                assert 'Command text: \'cmd' in logs.output[0]

    def test_only_all_logs_command(self):
        all_auth_filters = (only_real, only_owner, only_friends)
        for auth_filter in all_auth_filters:
            auth_filter_name = auth_filter.__name__
            with self.subTest(auth_filter_name=auth_filter_name):
                noop = auth_filter(lambda _update: True)
                update_mock = MagicMock()
                update_mock.message = None
                update_mock.effective_user = None
                with self.assertLogs(logger) as logs:
                    assert noop(update_mock) is None
                assert (
                    'Message received with no user '
                    f'trying to access a only_real command. '
                    'Command text: \'unknown\' (cropped to 10 chars).'
                ) in logs.output[0]

    def test_only_real_user_is_none(self):
        noop = only_real(lambda _update: True)
        update_mock = MagicMock()
        update_mock.effective_user = None
        update_mock.message.text = 'cmd'
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_user_is_bot(self):
        noop = only_real(lambda _update: True)
        update_mock = MagicMock()
        update_mock.effective_user.is_bot = True
        update_mock.effective_user.username = 'un'
        update_mock.effective_user.id = 'id'
        update_mock.message.text = 'cmd'
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert (
            'Bot with username un and id id '
            'tried to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_user_ok(self):
        noop = only_real(lambda _update: True)
        update_mock = MagicMock()
        update_mock.effective_user.is_bot = False
        assert noop(update_mock) is True

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_ok(self, _get_owner_id):
        noop = only_owner(lambda _update: True)
        update_mock = MagicMock()
        update_mock.effective_user.id = OWNER_USERID
        update_mock.effective_user.is_bot = False
        assert noop(update_mock) is True

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_no_owner(self, _get_owner_id):
        noop = only_owner(lambda _update: True)
        update_mock = MagicMock()
        update_mock.effective_user.id = UNKNOWN_USERID
        update_mock.effective_user.is_bot = False
        update_mock.effective_user.username = 'un'
        update_mock.effective_user.id = 'id'
        update_mock.message.text = 'cmd'
        with self.assertLogs(logger) as logs:
            assert noop(update_mock) is None
        assert (
            f'User un with id id '
            f'tried to access a only_owner command. '
            f'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_friends_is_friend(self):
        noop = only_friends(lambda _update: True)
        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            update_mock = MagicMock()
            update_mock.effective_user.id = FIRST_FRIEND_USERID
            update_mock.effective_user.is_bot = False
            assert noop(update_mock) is True

    def test_only_friends_not_friend(self):
        noop = only_friends(lambda _update: True)
        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            update_mock = MagicMock()
            update_mock.effective_user.id = UNKNOWN_USERID
            update_mock.effective_user.is_bot = False
            update_mock.effective_user.username = 'un'
            update_mock.effective_user.id = 'id'
            update_mock.message.text = 'cmd'
            with self.assertLogs(logger) as logs:
                assert noop(update_mock) is None
            assert (
                f'User un with id id '
                f'tried to access a only_friends command. '
                f'Command text: \'cmd\' (cropped to 10 chars).'
            ) in logs.output[0]

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
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                add_friend(FIRST_FRIEND_USERID)
                set_config.assert_called_once_with(CFG_KEY, JSON_FIRST_FRIEND)

    def test_auth_add_friend_already_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                add_friend(FIRST_FRIEND_USERID)
                set_config.assert_not_called()

    def test_auth_add_friend_is_owner(self):
        with self._with_owner_and_friends(None):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                add_friend(OWNER_USERID)
                set_config.assert_not_called()

    def test_auth_del_friend_not_friends(self):
        with self._with_owner_and_friends(None):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                del_friend(FIRST_FRIEND_USERID)
                set_config.assert_not_called()

    def test_auth_del_friend_not_a_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                del_friend(SECOND_FRIEND_USERID)
                set_config.assert_not_called()

    def test_auth_del_friend_one_friend(self):
        with self._with_owner_and_friends(JSON_TWO_FRIENDS):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                del_friend(FIRST_FRIEND_USERID)
                set_config.assert_called_once_with(CFG_KEY, JSON_SECOND_FRIEND)

    def test_auth_del_friend_last_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND):
            with patch(f'{MODULE_PATH}.set_config') as set_config:
                del_friend(FIRST_FRIEND_USERID)
                set_config.assert_called_once_with(CFG_KEY, JSON_NO_FRIENDS)
