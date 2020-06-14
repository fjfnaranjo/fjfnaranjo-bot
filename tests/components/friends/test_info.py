from unittest.mock import MagicMock, patch, sentinel

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from fjfnaranjobot.auth import friends
from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import SORRY_TEXT, User
from fjfnaranjobot.components.friends.info import (
    ADD_FRIEND,
    DEL_FRIEND,
    GET_ADD_OR_DEL,
    add_friend_handler,
    add_friend_id_handler,
    add_handler,
    cancel_handler,
    del_friend_handler,
    del_friend_id_handler,
    del_handler,
    friends_handler,
    logger,
)

from ...base import (
    LOG_BOT_UNAUTHORIZED_HEAD,
    LOG_FRIEND_UNAUTHORIZED_HEAD,
    LOG_NO_USER_HEAD,
    LOG_USER_UNAUTHORIZED_HEAD,
    BotHandlerTestCase,
    CallWithMarkup,
)

MODULE_PATH = 'fjfnaranjobot.components.friends.info'


@patch(f'{MODULE_PATH}.KEYBOARD_ROWS', 2)
class FriendsHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.chat_data = {'chat_id': 1, 'message_id': 2}
        self.user_is_owner()
        friends.clear()
        friends.add(User(1, '1un'))
        friends.add(User(2, '2un'))
        friends.add(User(3, '3un'))
        friends.add(User(4, '4un'))
        friends.add(User(5, '5un'))

        self.cancel_markup_dict = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
        ).to_dict()

        self.confirm_markup_dict = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Confirm", callback_data='confirm')],
                [InlineKeyboardButton("Cancel", callback_data='cancel')],
            ]
        ).to_dict()

        self.action_markup_dict = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("List", callback_data='list'),
                    InlineKeyboardButton("Add", callback_data='add'),
                    InlineKeyboardButton("Delete", callback_data='del'),
                ],
                [InlineKeyboardButton("Cancel", callback_data='cancel')],
            ]
        ).to_dict()

    def set_contact(self, id_, first_name, last_name):
        self._message_contact_mock = MagicMock()
        self._message_contact_mock.user_id = id_
        self._message_contact_mock.first_name = first_name
        self._message_contact_mock.last_name = last_name
        self._update_mock.message.contact = self._message_contact_mock

    def test_friends_handler_user_is_none(self):
        self.user_is_none()
        with self.assert_log_dispatch(LOG_NO_USER_HEAD, auth_logger):
            friends_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_friends_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assert_log_dispatch(LOG_USER_UNAUTHORIZED_HEAD, auth_logger):
            friends_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_friends_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assert_log_dispatch(LOG_BOT_UNAUTHORIZED_HEAD, auth_logger):
            friends_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_friends_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assert_log_dispatch(LOG_FRIEND_UNAUTHORIZED_HEAD, auth_logger):
            friends_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id_from_update, SORRY_TEXT)

    def test_friends_handler(self):
        self.chat_data = {}
        with self.assert_log('Entering friends conversation.', logger):
            assert GET_ADD_OR_DEL == friends_handler(*self.update_and_context)
        self.assert_reply_call(
            CallWithMarkup(
                (
                    'You can list all your friends. '
                    'Also, you can add or remove Telegram contacts and IDs to the list. '
                    'You can also cancel the friends command at any time.'
                ),
                reply_markup_dict=self.action_markup_dict,
            ),
        )
        assert {
            'chat_id': sentinel.chat_id_from_update,
            'message_id': sentinel.message_id_from_reply_text,
        } == self.chat_data

    def test_add_handler(self):
        with self.assert_log(
            'Requesting contact to add as a friend.', logger,
        ):
            assert ADD_FRIEND == add_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Send me the contact of the friend you want to add. Or its id.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )

    def test_add_friend_handler(self):
        self.set_contact(9, '9fn', '9ln')
        with self.assert_log('Received a contact. Adding 9fn 9ln as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Added 9fn 9ln as a friend.')
        assert {} == self.chat_data
        assert User(9, None) in friends

    def test_add_friend_handler_no_id(self):
        self.set_contact(None, 'nfn', 'nln')
        with self.assert_log('Received a contact without a Telegram ID.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That doesn\'t look like a Telegram user.')
        assert {} == self.chat_data

    def test_add_friend_handler_no_first_name(self):
        self.set_contact(9, None, '9ln')
        with self.assert_log('Adding 9ln as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Added 9ln as a friend.')
        assert {} == self.chat_data
        assert User(9, None) in friends

    def test_add_friend_handler_no_last_name(self):
        self.set_contact(9, '9fn', None)
        with self.assert_log('Adding 9fn as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Added 9fn as a friend.')
        assert {} == self.chat_data
        assert User(9, None) in friends

    def test_add_friend_handler_existing(self):
        self.set_contact(1, '1fna', '1lna')
        with self.assert_log('Adding 1fna 1lna as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Added 1fna 1lna as a friend.')
        assert {} == self.chat_data
        found = False
        for friend in friends:
            if friend.id == 1:
                found = True
                assert '1fna 1lna' == friend.username
        assert found

    def test_add_friend_id_handler_number_ok(self):
        self.set_string_command('9')
        with self.assert_log('Adding ID 9 as a friend.', logger):
            assert ConversationHandler.END == add_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Added ID 9 as a friend.')
        assert {} == self.chat_data
        assert User(9, None) in friends

    def test_add_friend_id_handler_number_multiple_str(self):
        self.set_string_command('9 9')
        with self.assert_log(
            'Received and invalid id \'9 9\' trying to add a friend.', logger
        ):
            assert ConversationHandler.END == add_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That\'s not a contact nor a single valid id.')

    def test_add_friend_id_handler_number_less_zero(self):
        self.set_string_command('-3')
        with self.assert_log(
            'Received and invalid number in id \'-3\' trying to add a friend.', logger
        ):
            assert ConversationHandler.END == add_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That\'s not a contact nor a valid id.')

    def test_del_handler(self):
        with self.assert_log(
            'Requesting contact to remove as a friend.', logger,
        ):
            assert DEL_FRIEND == del_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Send me the contact of the friend you want to remove. Or its id.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )

    def test_del_friend_handler(self):
        self.set_contact(1, '1fn', '1ln')
        with self.assert_log(
            'Removing 1un as a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Removed 1un as a friend.')
        assert {} == self.chat_data
        assert User(1, None) not in friends

    def test_del_friend_handler_no_id(self):
        self.set_contact(None, 'nfn', 'nln')
        with self.assert_log('Received a contact without a Telegram ID.', logger):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That doesn\'t look like a Telegram user.')

    def test_del_friend_handler_no_first_name(self):
        self.set_contact(1, None, '1ln')
        with self.assert_log(
            'Removing 1un as a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Removed 1un as a friend.')
        assert {} == self.chat_data
        assert User(1, None) not in friends

    def test_del_friend_handler_no_last_name(self):
        self.set_contact(1, '1fn', None)
        with self.assert_log(
            'Removing 1un as a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Removed 1un as a friend.')
        assert {} == self.chat_data
        assert User(1, None) not in friends

    def test_del_friend_handler_dont_exists(self):
        self.set_contact(9, '9fn', '9ln')
        with self.assert_log(
            'Not removing 9fn 9ln because its not a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, '9fn 9ln isn\'t a friend.')
        assert {} == self.chat_data

    def test_del_friend_id_handler_number_ok(self):
        self.set_string_command('1')
        with self.assert_log(
            'Removing 1un as a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Removed 1un as a friend.')
        assert {} == self.chat_data
        assert User(1, None) not in friends

    def test_del_friend_id_handler_number_multiple_str(self):
        self.set_string_command('9 9')
        with self.assert_log(
            'Received and invalid id \'9 9\' trying to remove a friend.', logger
        ):
            assert ConversationHandler.END == del_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That\'s not a contact nor a single valid id.')

    def test_del_friend_id_handler_number_less_zero(self):
        self.set_string_command('-3')
        with self.assert_log(
            'Received and invalid number in id \'-3\' trying to remove a friend.',
            logger,
        ):
            assert ConversationHandler.END == del_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'That\'s not a contact nor a valid id.')

    def test_cancel_handler(self):
        self.chat_data.update(
            {
                'chat_id': 1,
                'message_id': 2,
                'delete_user': 'delete_user',
                'keyboard_users': 'keyboard_users',
                'offset': 0,
                'some': 'content',
            }
        )
        with self.assert_log(
            'Abort friends conversation.', logger,
        ):
            assert ConversationHandler.END == cancel_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Ok.')
        assert {'some': 'content'} == self.chat_data
