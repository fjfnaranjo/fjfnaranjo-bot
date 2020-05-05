from unittest.mock import patch, MagicMock

from telegram.ext import DispatcherHandlerStop
from pytest import raises

from fjfnaranjobot.components.friends.use_cases import friends
from tests.base import BotTestCase


MODULE_PATH = 'fjfnaranjobot.components.friends.use_cases'
# get_friends, add_friend, del_friend, only_owner
# friends


class FriendsUseCasesTests(BotTestCase):
    def _update_with_no_user(self, update):
        update.effective_user = None
        return update

    def _update_with_user_bot(self, update):
        update.effective_user.is_bot = True
        update.effective_user.id = 999
        return update

    def _update_with_user_friend(self, update, id_):
        update.effective_user.is_bot = False
        update.effective_user.id = id_
        return update

    def _update_with_user_owner(self, update):
        update.effective_user.is_bot = False
        update.effective_user.id = 99
        return update

    def test_friends_no_user(self):
        update = MagicMock()
        self._update_with_no_user(update)
        returned = friends(update, None)
        assert returned is None

    def test_friends_bot_user(self):
        update = MagicMock()
        self._update_with_user_bot(update)
        returned = friends(update, None)
        assert returned is None

    @patch(f'{MODULE_PATH}.get_friends', return_value=['2'])
    def test_friends_friend_user(self, _get_friends):
        update = MagicMock()
        self._update_with_user_friend(update, 2)
        returned = friends(update, None)
        assert returned is None

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    def test_friends_no_friends(self, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('You don\'t have', message)

    @patch(f'{MODULE_PATH}.get_friends', return_value=['2'])
    def test_friends_one_friend(self, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn(': 2', message)

    @patch(f'{MODULE_PATH}.get_friends', return_value=['2', '3'])
    def test_friends_many_friends(self, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('2', message)
        self.assertIn('3', message)

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_no_friends(self, add_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd add 2'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Added', message)
        self.assertIn('2', message)
        add_friend.assert_called_once_with('2')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[2])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_some_friends(self, add_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd add 3'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Added', message)
        self.assertIn('3', message)
        add_friend.assert_called_once_with('3')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[2])
    @patch(f'{MODULE_PATH}.add_friend')
    def test_friends_add_already_friend(self, add_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd add 2'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Added', message)
        self.assertIn('2', message)
        add_friend.assert_called_once_with('2')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_no_friends(self, del_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd del 2'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Removed', message)
        self.assertIn('2', message)
        del_friend.assert_called_once_with('2')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[2])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_not_friends(self, del_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd del 3'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Removed', message)
        self.assertIn('3', message)
        del_friend.assert_called_once_with('3')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[2, 3])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_some_friends(self, del_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd del 3'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Removed', message)
        self.assertIn('3', message)
        del_friend.assert_called_once_with('3')

    @patch(f'{MODULE_PATH}.get_friends', return_value=[2])
    @patch(f'{MODULE_PATH}.del_friend')
    def test_friends_del_last_friend(self, del_friend, _get_friends):
        update = MagicMock()
        update.message.text = f'cmd del 2'
        self._update_with_user_owner(update)
        with raises(DispatcherHandlerStop):
            friends(update, None)
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        self.assertIn('Removed', message)
        self.assertIn('2', message)
        del_friend.assert_called_once_with('2')
