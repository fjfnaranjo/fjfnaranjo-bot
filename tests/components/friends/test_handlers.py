from unittest.mock import patch

from fjfnaranjobot.components.friends.handlers import (
    friends_add_handler,
    friends_del_handler,
    friends_get_handler,
    logger,
)

from ...base import (
    FIRST_FRIEND_USERID,
    SECOND_FRIEND_USERID,
    THIRD_FRIEND_USERID,
    BotHandlerTestCase,
)

MODULE_PATH = 'fjfnaranjobot.components.friends.handlers'


class FriendsHandlersTests(BotHandlerTestCase):
    def setUp(self):
        BotHandlerTestCase.setUp(self)
        self.user_is_owner()

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_get_no_friends(self, _get_friends):
        self.set_string_command('friends_get')
        with self.assert_log_dispatch('Sending no friends.', logger):
            friends_get_handler(*self.update_and_context)
        self.assert_reply('You don\'t have any friends.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    def test_friends_get_one_friend(self, _get_friends):
        self.set_string_command('friends_get')
        with self.assert_log_dispatch('Sending one friend.', logger):
            friends_get_handler(*self.update_and_context)
        self.assert_reply(f'You only have one friend: \'{FIRST_FRIEND_USERID}\'.')

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    def test_friends_get_two_friends(self, _get_friends):
        self.set_string_command('friends_get')
        with self.assert_log_dispatch('Sending two friends.', logger):
            friends_get_handler(*self.update_and_context)
        self.assert_reply(
            f'You have two friends: \'{FIRST_FRIEND_USERID}\' and \'{SECOND_FRIEND_USERID}\'.'
        )

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID, THIRD_FRIEND_USERID],
    )
    def test_friends_get_many_friends(self, _get_friends):
        self.set_string_command('friends_get')
        with self.assert_log_dispatch('Sending list of friends.', logger):
            friends_get_handler(*self.update_and_context)
        self.assert_reply(
            (
                f'Your friends are: \'{FIRST_FRIEND_USERID}\', '
                f'\'{SECOND_FRIEND_USERID}\' and \'{THIRD_FRIEND_USERID}\'.'
            )
        )

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_get_no_extra_params(self, _get_friends):
        self.set_string_command('friends_get', ['arg'])
        with self.assertRaises(ValueError) as e:
            friends_get_handler(*self.update_and_context)
        assert (
            '\'friends_get\' command doesn\'t accept arguments.' == e.exception.args[0]
        )

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_no_friends(self, add_friend, _get_friends):
        self.set_string_command('friends_add', [f'{FIRST_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Adding @{FIRST_FRIEND_USERID} as a friend.', logger
        ):
            friends_add_handler(*self.update_and_context)
        add_friend.assert_called_once_with(FIRST_FRIEND_USERID)
        self.assert_reply(f'Added @{FIRST_FRIEND_USERID} as a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_some_friends(self, add_friend, _get_friends):
        self.set_string_command('friends_add', [f'{SECOND_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Adding @{SECOND_FRIEND_USERID} as a friend.', logger
        ):
            friends_add_handler(*self.update_and_context)
        add_friend.assert_called_once_with(SECOND_FRIEND_USERID)
        self.assert_reply(f'Added @{SECOND_FRIEND_USERID} as a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_already_friend(self, add_friend, _get_friends):
        self.set_string_command('friends_add', [f'{FIRST_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Not adding @{FIRST_FRIEND_USERID} because already a friend.', logger
        ):
            friends_add_handler(*self.update_and_context)
        add_friend.assert_not_called()
        self.assert_reply(f'@{FIRST_FRIEND_USERID} is already a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_add_not_int(self, _get_friends):
        self.set_string_command('friends_add', ['a'])
        with self.assertRaises(ValueError) as e:
            friends_add_handler(*self.update_and_context)
        assert 'Error parsing id as int.' == e.exception.args[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_add_no_extra_params(self, _get_friends):
        self.set_string_command('friends_add', ['2', '3'])
        with self.assertRaises(ValueError) as e:
            friends_add_handler(*self.update_and_context)
        assert 'too many values to unpack (expected 1)' == e.exception.args[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_no_friends(self, del_friend, _get_friends):
        self.set_string_command('friends_del', [f'{FIRST_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Not removing @{FIRST_FRIEND_USERID} because not a friend.', logger
        ):
            friends_del_handler(*self.update_and_context)
        del_friend.assert_not_called()
        self.assert_reply(f'@{FIRST_FRIEND_USERID} isn\'t a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_not_friends(self, del_friend, _get_friends):
        self.set_string_command('friends_del', [f'{SECOND_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Not removing @{SECOND_FRIEND_USERID} because not a friend.', logger
        ):
            friends_del_handler(*self.update_and_context)
        del_friend.assert_not_called()
        self.assert_reply(f'@{SECOND_FRIEND_USERID} isn\'t a friend.')

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_some_friends(self, del_friend, _get_friends):
        self.set_string_command('friends_del', [f'{SECOND_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Removing @{SECOND_FRIEND_USERID} as a friend.', logger
        ):
            friends_del_handler(*self.update_and_context)
        del_friend.assert_called_once_with(SECOND_FRIEND_USERID)
        self.assert_reply(f'Removed @{SECOND_FRIEND_USERID} as a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_last_friend(self, del_friend, _get_friends):
        self.set_string_command('friends_del', [f'{FIRST_FRIEND_USERID}'])
        with self.assert_log_dispatch(
            f'Removing @{FIRST_FRIEND_USERID} as a friend.', logger
        ):
            friends_del_handler(*self.update_and_context)
        del_friend.assert_called_once_with(FIRST_FRIEND_USERID)
        self.assert_reply(f'Removed @{FIRST_FRIEND_USERID} as a friend.')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_del_not_int(self, _get_friends):
        self.set_string_command('friends_del', ['a'])
        with self.assertRaises(ValueError) as e:
            friends_del_handler(*self.update_and_context)
        assert 'Error parsing id as int.' == e.exception.args[0]

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_del_no_extra_params(self, _get_friends):
        self.set_string_command('friends_del', ['2', '3'])
        with self.assertRaises(ValueError) as e:
            friends_del_handler(*self.update_and_context)
        assert 'too many values to unpack (expected 1)' == e.exception.args[0]
