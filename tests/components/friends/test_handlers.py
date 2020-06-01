from unittest.mock import MagicMock, patch

from telegram.ext import ConversationHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import friends
from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import User
from fjfnaranjobot.components.friends.handlers import (
    ADD_FRIEND,
    DEL_FRIEND,
    GET_ADD_OR_DEL,
    GET_PAGE,
    ONLY_PAGE,
    add_friend_handler,
    add_friend_id_handler,
    add_handler,
    cancel_handler,
    del_friend_handler,
    del_friend_id_handler,
    del_handler,
    friends_handler,
    get_page_handler,
    logger,
)

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.friends.handlers'


@patch(f'{MODULE_PATH}.PAGE_SIZE', 2)
class FriendsHandlersTests(BotHandlerTestCase):
    def setUp(self):
        BotHandlerTestCase.setUp(self)
        self.user_data = {'message_ids': (1, 2)}
        self.user_is_owner()
        friends.clear()
        friends.add(User(1, '1un'))
        friends.add(User(2, '2un'))
        friends.add(User(3, '3un'))
        friends.add(User(4, '4un'))
        friends.add(User(5, '5un'))

    def set_contact(self, id_, first_name, last_name):
        self._message_contact_mock = MagicMock()
        self._message_contact_mock.user_id = id_
        self._message_contact_mock.first_name = first_name
        self._message_contact_mock.last_name = last_name
        self._update_mock.message.contact = self._message_contact_mock

    def test_config_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_config_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_config_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assertLogs(auth_logger) as logs:
            with self.assertRaises(DispatcherHandlerStop):
                friends_handler(*self.update_and_context)
        assert 1 == len(logs.output)

    def test_friends_handler(self):
        self.user_data = {}
        with self.assert_log('Entering friends conversation.', logger):
            assert GET_ADD_OR_DEL == friends_handler(*self.update_and_context)
        self.assert_reply(
            (
                'If you want to see your friends, use /friends_getpage . '
                'If you want to add a friend, /friends_add . '
                'If you want to remove a friend, /friends_del . '
                'If you want to do something else, /friends_cancel .'
            )
        )
        assert {
            'message_ids': (
                self.message_reply_text.chat.id,
                self.message_reply_text.message_id,
            )
        } == self.user_data

    def test_get_page_handler_arg_is_not_number(self):
        self.set_string_command('/friends_getpage', ['a'])
        with self.assert_log('Received an invalid page number \'a\'.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'The page \'a\' is not a valid page number. '
            'Send the /friends_getpage command to request more pages (if aplicable).'
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_get_page_handler_arg_is_zero(self):
        self.set_string_command('/friends_getpage', ['0'])
        with self.assert_log('Received an invalid page number \'0\'.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'The page \'0\' is not a valid page number. '
            'Send the /friends_getpage command to request more pages (if aplicable).'
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_get_page_handler_arg_minus_one(self):
        self.set_string_command('/friends_getpage', ['-1'])
        with self.assert_log('Received an invalid page number \'-1\'.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'The page \'-1\' is not a valid page number. '
            'Send the /friends_getpage command to request more pages (if aplicable).'
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_get_page_handler_dont_exists_in_args(self):
        self.set_string_command('/friends_getpage', ['4'])
        with self.assert_log(
            'Not sending the page 4 of friends because it doesn\'t exists.', logger
        ):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'The page 4 doesn\'t exists. '
            'Send the /friends_getpage command again to start from the first page.'
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )
        assert 'page' not in self.user_data

    def test_get_page_handler_last_page_in_command(self):
        self.set_string_command('/friends_getpage', ['3'])
        with self.assert_log('Sending the last page (page 3) of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the last page (page 3) of your friends list. '
            'Send the /friends_getpage command again to start from the first page.'
            'If you want to do something else, /friends_cancel .'
            '\n\n5un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 1 == self.user_data['page']

    def test_get_page_handler_last_page_in_context(self):
        self.user_data.update({'page': 3})
        with self.assert_log('Sending the last page (page 3) of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the last page (page 3) of your friends list. '
            'Send the /friends_getpage command again to start from the first page.'
            'If you want to do something else, /friends_cancel .'
            '\n\n5un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 1 == self.user_data['page']

    def test_get_page_handler_only_page(self):
        friends.clear()
        friends.add(User(1, '1un'))
        friends.add(User(2, '2un'))
        with self.assert_log('Sending the only page of friends.', logger):
            assert ONLY_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the only page of your friends list. '
            'If you want to do something else, /friends_cancel .'
            '\n\n1un\n2un',
            1,
            2,
        )
        assert 'page' not in self.user_data

    def test_get_page_handler_only_page_in_command(self):
        friends.clear()
        friends.add(User(1, '1un'))
        friends.add(User(2, '2un'))
        self.set_string_command('/friends_getpage', ['1'])
        with self.assert_log('Sending the only page of friends.', logger):
            assert ONLY_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the only page of your friends list. '
            'If you want to do something else, /friends_cancel .'
            '\n\n1un\n2un',
            1,
            2,
        )
        assert 'page' not in self.user_data

    def test_get_page_handler_first_page(self):
        with self.assert_log('Sending the first page of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the first page of your friends list. '
            'Send the /friends_getpage command to request more pages.'
            'If you want to do something else, /friends_cancel .'
            '\n\n1un\n2un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 2 == self.user_data['page']

    def test_get_page_handler_first_page_in_command(self):
        self.set_string_command('/friends_getpage', ['1'])
        with self.assert_log('Sending the first page of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the first page of your friends list. '
            'Send the /friends_getpage command to request more pages.'
            'If you want to do something else, /friends_cancel .'
            '\n\n1un\n2un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 2 == self.user_data['page']

    def test_get_page_handler_first_page_in_context(self):
        self.user_data.update({'page': 1})
        with self.assert_log('Sending the first page of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the first page of your friends list. '
            'Send the /friends_getpage command to request more pages.'
            'If you want to do something else, /friends_cancel .'
            '\n\n1un\n2un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 2 == self.user_data['page']

    def test_get_page_handler_second_page_in_command(self):
        self.set_string_command('/friends_getpage', ['2'])
        with self.assert_log('Sending the page 2 of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the page 2 of your friends list. '
            'Send the /friends_getpage command to request more pages.'
            'If you want to do something else, /friends_cancel .'
            '\n\n3un\n4un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 3 == self.user_data['page']

    def test_get_page_handler_second_page_in_context(self):
        self.user_data.update({'page': 2})
        with self.assert_log('Sending the page 2 of friends.', logger):
            assert GET_PAGE == get_page_handler(*self.update_and_context)
        self.assert_edit(
            'This is the page 2 of your friends list. '
            'Send the /friends_getpage command to request more pages.'
            'If you want to do something else, /friends_cancel .'
            '\n\n3un\n4un',
            1,
            2,
        )
        assert 'page' in self.user_data
        assert 3 == self.user_data['page']

    def test_add_handler(self):
        with self.assert_log(
            'Requesting contact to add as a friend.', logger,
        ):
            assert ADD_FRIEND == add_handler(*self.update_and_context)
        self.assert_edit(
            'Send me the contact of the friend you want to add. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_add_friend_handler(self):
        self.set_contact(9, '9fn', '9ln')
        with self.assert_log('Adding 9fn 9ln as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_reply('Added 9fn 9ln as a friend.')
        assert {} == self.user_data
        assert User(9, None) in friends

    def test_add_friend_handler_existing(self):
        self.set_contact(1, '1fna', '1lna')
        with self.assert_log('Adding 1fna 1lna as a friend.', logger):
            assert ConversationHandler.END == add_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_reply('Added 1fna 1lna as a friend.')
        assert {} == self.user_data
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
        self.assert_reply('Added ID 9 as a friend.')
        assert {} == self.user_data
        assert User(9, None) in friends

    def test_add_friend_id_handler_number_multiple_str(self):
        self.set_string_command('9 9')
        with self.assert_log(
            'Received and invalid id \'9 9\' trying to add a friend.', logger
        ):
            assert ADD_FRIEND == add_friend_id_handler(*self.update_and_context)
        self.assert_edit(
            'That\'s not a contact nor a single valid id. '
            'Send me the contact of the friend you want to add. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_add_friend_id_handler_number_less_zero(self):
        self.set_string_command('-3')
        with self.assert_log(
            'Received and invalid number in id \'-3\' trying to add a friend.', logger
        ):
            assert ADD_FRIEND == add_friend_id_handler(*self.update_and_context)
        self.assert_edit(
            'That\'s not a contact nor a valid id. '
            'Send me the contact of the friend you want to add. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_del_handler(self):
        with self.assert_log(
            'Requesting contact to remove as a friend.', logger,
        ):
            assert DEL_FRIEND == del_handler(*self.update_and_context)
        self.assert_edit(
            'Send me the contact of the friend you want to remove. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
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
        self.assert_reply('Removed 1un as a friend.')
        assert {} == self.user_data
        assert User(1, None) not in friends

    def test_del_friend_handler_dont_exists(self):
        self.set_contact(9, '9fn', '9ln')
        with self.assert_log(
            'Not removing 9fn 9ln because not a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_reply('9fn 9ln isn\'t a friend.')
        assert {} == self.user_data

    def test_del_friend_id_handler_number_ok(self):
        self.set_string_command('1')
        with self.assert_log(
            'Removing 1un as a friend.', logger,
        ):
            assert ConversationHandler.END == del_friend_id_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_reply('Removed 1un as a friend.')
        assert {} == self.user_data
        assert User(1, None) not in friends

    def test_del_friend_id_handler_number_multiple_str(self):
        self.set_string_command('9 9')
        with self.assert_log(
            'Received and invalid id \'9 9\' trying to remove a friend.', logger
        ):
            assert DEL_FRIEND == del_friend_id_handler(*self.update_and_context)
        self.assert_edit(
            'That\'s not a contact nor a single valid id. '
            'Send me the contact of the friend you want to remove. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_del_friend_id_handler_number_less_zero(self):
        self.set_string_command('-3')
        with self.assert_log(
            'Received and invalid number in id \'-3\' trying to remove a friend.',
            logger,
        ):
            assert DEL_FRIEND == del_friend_id_handler(*self.update_and_context)
        self.assert_edit(
            'That\'s not a contact nor a valid id. '
            'Send me the contact of the friend you want to remove. '
            'Or its id. '
            'If you want to do something else, /friends_cancel .',
            1,
            2,
        )

    def test_cancel_handler(self):
        self.user_data.update({'page': 0, 'some': 'content'})
        with self.assert_log(
            'Abort friends conversation.', logger,
        ):
            assert ConversationHandler.END == cancel_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_reply('Ok.')
        assert {'some': 'content'} == self.user_data
