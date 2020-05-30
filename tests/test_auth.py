from contextlib import contextmanager
from unittest.mock import patch

from telegram.ext.dispatcher import DispatcherHandlerStop

from fjfnaranjobot.auth import (
    CFG_KEY,
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

from .base import (
    BOT_USERID,
    FIRST_FRIEND_USERID,
    JSON_FIRST_FRIEND,
    JSON_ONE_FRIEND,
    JSON_SECOND_FRIEND,
    JSON_TWO_FRIENDS,
    OWNER_USERID,
    SECOND_FRIEND_USERID,
    UNKNOWN_USERID,
    BotUpdateContextTestCase,
)

MODULE_PATH = 'fjfnaranjobot.auth'


class AuthTests(BotUpdateContextTestCase):
    @contextmanager
    def _with_owner_and_friends(self, friends_list):
        fake_config = {CFG_KEY: friends_list} if friends_list is not None else {}
        with patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID):
            with patch(f'{MODULE_PATH}.config', fake_config):
                yield fake_config

    def test_get_owner_id_no_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', None, ['BOT_OWNER_ID']
        ):
            with self.assertRaises(ValueError) as e:
                get_owner_id()
            assert 'BOT_OWNER_ID var must be defined.' == e.exception.args[0]

    def test_get_owner_id_env_not_int(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': 'a'}):
            with self.assertRaises(ValueError) as e:
                get_owner_id()
            assert 'Invalid id in BOT_OWNER_ID var.' == e.exception.args[0]

    def test_get_owner_id_env(self):
        with self._with_mocked_environ(f'{MODULE_PATH}.environ', {'BOT_OWNER_ID': '1'}):
            assert get_owner_id() == 1

    def test_ensure_int_ok(self):
        ensured = ensure_int('53')
        assert ensured == 53
        assert isinstance(ensured, int)

    def test_ensure_int_empty(self):
        with self.assertRaises(ValueError) as e:
            ensure_int('')
        assert 'Error parsing id as int.' == e.exception.args[0]

    def test_ensure_int_not_int(self):
        with self.assertRaises(ValueError):
            ensure_int('one')

    def test_only_real_no_user_no_message(self):
        noop = only_real(lambda _update: True)
        self.user_is_none(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_no_user_empty_command(self):
        noop = only_real(lambda _update: True)
        self.user_is_none(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_no_user(self):
        noop = only_real(lambda _update: True)
        self.user_is_none()
        self.set_string_command('cmd')
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            'Message received with no user '
            'trying to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot_no_message(self):
        noop = only_real(lambda _update: True)
        self.user_is_bot(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'Bot with username bot and id {BOT_USERID} '
            'tried to access a only_real command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot_empty_command(self):
        noop = only_real(lambda _update: True)
        self.user_is_bot(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'Bot with username bot and id {BOT_USERID} '
            'tried to access a only_real command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_bot(self):
        noop = only_real(lambda _update: True)
        self.user_is_bot()
        self.set_string_command('cmd')
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'Bot with username bot and id {BOT_USERID} '
            'tried to access a only_real command. '
            'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_real_user_ok(self):
        noop = only_real(lambda _update: True)
        self.user_is_unknown()
        assert noop(self.update) is True

    def test_only_owner_no_message(self):
        noop = only_owner(lambda _update: True)
        self.user_is_unknown(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'User unknown with id {UNKNOWN_USERID} '
            'tried to access a only_owner command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_owner_empty_command(self):
        noop = only_owner(lambda _update: True)
        self.user_is_unknown(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'User unknown with id {UNKNOWN_USERID} '
            'tried to access a only_owner command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_no_owner(self, _get_owner_id):
        noop = only_owner(lambda _update: True)
        self.user_is_unknown()
        self.set_string_command('cmd')
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                assert noop(self.update) is None
        assert (
            f'User unknown with id {UNKNOWN_USERID} '
            f'tried to access a only_owner command. '
            f'Command text: \'cmd\' (cropped to 10 chars).'
        ) in logs.output[0]

    @patch(f'{MODULE_PATH}.get_owner_id', return_value=OWNER_USERID)
    def test_only_owner_ok(self, _get_owner_id):
        noop = only_owner(lambda _update: True)
        self.user_is_owner()
        assert noop(self.update) is True

    def test_only_friends_no_message(self):
        noop = only_friends(lambda _update: True)
        self.user_is_unknown(True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'User unknown with id {UNKNOWN_USERID} '
            'tried to access a only_friends command. '
            'Command text: \'<unknown>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_friends_empty_command(self):
        noop = only_friends(lambda _update: True)
        self.user_is_unknown(None, True)
        with self.assertLogs(logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                noop(self.update)
        assert (
            f'User unknown with id {UNKNOWN_USERID} '
            'tried to access a only_friends command. '
            'Command text: \'<empty>\' (cropped to 10 chars).'
        ) in logs.output[0]

    def test_only_friends_not_friend(self):
        noop = only_friends(lambda _update: True)
        self.user_is_unknown()
        self.set_string_command('cmd')
        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            with self.assertLogs(logger) as logs:
                with self.assertRaises(DispatcherHandlerStop):
                    noop(self.update)
            assert (
                f'User unknown with id {UNKNOWN_USERID} '
                f'tried to access a only_friends command. '
                f'Command text: \'cmd\' (cropped to 10 chars).'
            ) in logs.output[0]

    def test_only_friends_ok(self):
        noop = only_friends(lambda _update: True)
        self.user_is_friend()
        with self._with_owner_and_friends(JSON_FIRST_FRIEND):
            assert noop(self.update) is True

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
        with self._with_owner_and_friends(None) as config:
            add_friend(FIRST_FRIEND_USERID)
            assert JSON_FIRST_FRIEND == config[CFG_KEY]

    def test_auth_add_friend_already_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND) as config:
            add_friend(FIRST_FRIEND_USERID)
            assert JSON_FIRST_FRIEND == config[CFG_KEY]

    def test_auth_add_friend_is_owner(self):
        with self._with_owner_and_friends(None) as config:
            add_friend(OWNER_USERID)
            assert CFG_KEY not in config

    def test_auth_del_friend_not_friends(self):
        with self._with_owner_and_friends(None) as config:
            del_friend(FIRST_FRIEND_USERID)
            assert CFG_KEY not in config

    def test_auth_del_friend_not_a_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND) as config:
            del_friend(SECOND_FRIEND_USERID)
            assert JSON_FIRST_FRIEND == config[CFG_KEY]

    def test_auth_del_friend_one_friend(self):
        with self._with_owner_and_friends(JSON_TWO_FRIENDS) as config:
            del_friend(FIRST_FRIEND_USERID)
            assert JSON_SECOND_FRIEND == config[CFG_KEY]

    def test_auth_del_friend_last_friend(self):
        with self._with_owner_and_friends(JSON_ONE_FRIEND) as config:
            del_friend(FIRST_FRIEND_USERID)
            assert CFG_KEY not in config
