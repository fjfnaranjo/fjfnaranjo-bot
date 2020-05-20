from unittest.mock import patch

from fjfnaranjobot.components.friends.use_cases import friends

from ...base import FIRST_FRIEND_USERID, SECOND_FRIEND_USERID, BotUseCaseTestCase

MODULE_PATH = 'fjfnaranjobot.components.friends.use_cases'


class FriendsUseCasesTests(BotUseCaseTestCase):
    def test_friends_no_user(self):
        self._user_is_none()
        returned = friends(self.update, None)
        assert returned is None

    def test_friends_bot_user(self):
        self._user_is_bot()
        returned = friends(self.update, None)
        assert returned is None

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    def test_friends_friend_user(self, _get_friends):
        self._user_is_friend(FIRST_FRIEND_USERID)
        returned = friends(self.update, None)
        assert returned is None

    def test_friends_invalid_syntax_usage(self):
        self._set_msg('cmd add add add')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Invalid syntax' in message

    def test_friends_invalid_syntax_subcommand(self):
        self._set_msg('cmd invalid 0')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Unknown sub-command' in message

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_no_friends(self, _get_friends):
        self._set_msg('cmd')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'You don\'t have' in message

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    def test_friends_one_friend(self, _get_friends):
        self._set_msg('cmd')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert str(FIRST_FRIEND_USERID) in message

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    def test_friends_many_friends(self, _get_friends):
        self._set_msg('cmd')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert str(FIRST_FRIEND_USERID) in message
        assert str(SECOND_FRIEND_USERID) in message

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_no_friends(self, add_friend, _get_friends):
        self._set_msg(f'cmd add {FIRST_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Added' in message
        assert str(FIRST_FRIEND_USERID) in message
        add_friend.assert_called_once_with(FIRST_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_some_friends(self, add_friend, _get_friends):
        self._set_msg(f'cmd add {SECOND_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Added' in message
        assert str(SECOND_FRIEND_USERID) in message
        add_friend.assert_called_once_with(SECOND_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_already_friend(self, _add_friend, _get_friends):
        self._set_msg(f'cmd add {FIRST_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'already' in message
        assert str(FIRST_FRIEND_USERID) in message

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_no_friends(self, _del_friend, _get_friends):
        self._set_msg(f'cmd del {FIRST_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'isn' in message
        assert str(FIRST_FRIEND_USERID) in message

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_not_friends(self, _del_friend, _get_friends):
        self._set_msg(f'cmd del {SECOND_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'isn' in message
        assert str(SECOND_FRIEND_USERID) in message

    @patch(
        f'{MODULE_PATH}.get_friends',
        return_value=[FIRST_FRIEND_USERID, SECOND_FRIEND_USERID],
    )
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_some_friends(self, del_friend, _get_friends):
        self._set_msg(f'cmd del {SECOND_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Removed' in message
        assert str(SECOND_FRIEND_USERID) in message
        del_friend.assert_called_once_with(SECOND_FRIEND_USERID)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[FIRST_FRIEND_USERID])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_last_friend(self, del_friend, _get_friends):
        self._set_msg(f'cmd del {FIRST_FRIEND_USERID}')
        self._user_is_owner()
        with self._raises_dispatcher_stop():
            friends(self.update, None)
        self.update.message.reply_text.assert_called_once()
        message = self.update.message.reply_text.call_args[0][0]
        assert 'Removed' in message
        assert str(FIRST_FRIEND_USERID) in message
        del_friend.assert_called_once_with(FIRST_FRIEND_USERID)
