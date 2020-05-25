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
        self._user_is_owner()

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_get_no_friends(self, _get_friends):
        self._set_update_message_text('friends_get', [])
        with self._assert_reply_log_dispatch(
            'You don\'t have any friends.', 'Sending no friends.', logger
        ):
            friends_get_handler(self._update, None)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    def test_friends_get_one_friend(self, _get_friends):
        self._set_update_message_text('friends_get', [])
        with self._assert_reply_log_dispatch(
            f'You only have one friend: \'{FIRST_FRIEND_USERID}\'.',
            'Sending one friend.',
            logger,
        ):
            friends_get_handler(self._update, None)

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    def test_friends_get_two_friends(self, _get_friends):
        self._set_update_message_text('friends_get', [])
        with self._assert_reply_log_dispatch(
            f'You have two friends: \'{FIRST_FRIEND_USERID}\' and \'{SECOND_FRIEND_USERID}\'.',
            'Sending two friends.',
            logger,
        ):
            friends_get_handler(self._update, None)

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID, THIRD_FRIEND_USERID],
    )
    def test_friends_get_many_friends(self, _get_friends):
        self._set_update_message_text('friends_get', [])
        with self._assert_reply_log_dispatch(
            (
                f'Your friends are: \'{FIRST_FRIEND_USERID}\', '
                f'\'{SECOND_FRIEND_USERID}\' and \'{THIRD_FRIEND_USERID}\'.'
            ),
            'Sending list of friends.',
            logger,
        ):
            friends_get_handler(self._update, None)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_no_friends(self, add_friend, _get_friends):
        self._set_update_message_text('friends_add', [f'{FIRST_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'Added @{FIRST_FRIEND_USERID} as a friend.',
            f'Adding @{FIRST_FRIEND_USERID} as a friend.',
            logger,
        ):
            friends_add_handler(self._update, None)
        add_friend.assert_called_once_with(FIRST_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_some_friends(self, add_friend, _get_friends):
        self._set_update_message_text('friends_add', [f'{SECOND_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'Added @{SECOND_FRIEND_USERID} as a friend.',
            f'Adding @{SECOND_FRIEND_USERID} as a friend.',
            logger,
        ):
            friends_add_handler(self._update, None)
        add_friend.assert_called_once_with(SECOND_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_already_friend(self, add_friend, _get_friends):
        self._set_update_message_text('friends_add', [f'{FIRST_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'@{FIRST_FRIEND_USERID} is already a friend.',
            f'Not adding @{FIRST_FRIEND_USERID} because already a friend.',
            logger,
        ):
            friends_add_handler(self._update, None)
        add_friend.assert_not_called()

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_no_friends(self, del_friend, _get_friends):
        self._set_update_message_text('friends_del', [f'{FIRST_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'@{FIRST_FRIEND_USERID} isn\'t a friend.',
            f'Not removing @{FIRST_FRIEND_USERID} because not a friend.',
            logger,
        ):
            friends_del_handler(self._update, None)
        del_friend.assert_not_called()

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_not_friends(self, del_friend, _get_friends):
        self._set_update_message_text('friends_del', [f'{SECOND_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'@{SECOND_FRIEND_USERID} isn\'t a friend.',
            f'Not removing @{SECOND_FRIEND_USERID} because not a friend.',
            logger,
        ):
            friends_del_handler(self._update, None)
        del_friend.assert_not_called()

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_some_friends(self, del_friend, _get_friends):
        self._set_update_message_text('friends_del', [f'{SECOND_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'Removed @{SECOND_FRIEND_USERID} as a friend.',
            f'Removing @{SECOND_FRIEND_USERID} as a friend.',
            logger,
        ):
            friends_del_handler(self._update, None)
        del_friend.assert_called_once_with(SECOND_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_last_friend(self, del_friend, _get_friends):
        self._set_update_message_text('friends_del', [f'{FIRST_FRIEND_USERID}'])
        with self._assert_reply_log_dispatch(
            f'Removed @{FIRST_FRIEND_USERID} as a friend.',
            f'Removing @{FIRST_FRIEND_USERID} as a friend.',
            logger,
        ):
            friends_del_handler(self._update, None)
        del_friend.assert_called_once_with(FIRST_FRIEND_USERID)
