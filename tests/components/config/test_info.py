from unittest.mock import patch, sentinel

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.components.config.info import (
    DEL_VAR,
    GET_SET_OR_DEL,
    GET_VAR,
    SET_VALUE,
    SET_VAR,
    cancel_handler,
    config_handler,
    del_handler,
    del_var_handler,
    get_handler,
    get_var_handler,
    logger,
    set_handler,
    set_value_handler,
    set_var_handler,
)

from ...base import (
    LOG_BOT_UNAUTHORIZED_HEAD,
    LOG_FRIEND_UNAUTHORIZED_HEAD,
    LOG_NO_USER_HEAD,
    LOG_USER_UNAUTHORIZED_HEAD,
    BotHandlerTestCase,
    CallWithMarkup,
)

MODULE_PATH = 'fjfnaranjobot.components.config.info'


class ConfigHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.chat_data = {'chat_id': 1, 'message_id': 2}
        self.user_is_owner()

        self.cancel_markup_dict = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
        ).to_dict()

        self.action_markup_dict = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Get", callback_data='get'),
                    InlineKeyboardButton("Set", callback_data='set'),
                    InlineKeyboardButton("Delete", callback_data='del'),
                ],
                [InlineKeyboardButton("Cancel", callback_data='cancel')],
            ]
        ).to_dict()

    def test_config_handler_user_is_none(self):
        self.user_is_none()
        with self.assert_log_dispatch(LOG_NO_USER_HEAD, auth_logger):
            config_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_config_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assert_log_dispatch(LOG_USER_UNAUTHORIZED_HEAD, auth_logger):
            config_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_config_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assert_log_dispatch(LOG_BOT_UNAUTHORIZED_HEAD, auth_logger):
            config_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_config_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assert_log_dispatch(LOG_FRIEND_UNAUTHORIZED_HEAD, auth_logger):
            config_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_config_handler(self):
        self.chat_data = {}
        with self.assert_log('Entering config conversation.', logger):
            assert GET_SET_OR_DEL == config_handler(*self.update_and_context)
        self.assert_message_call(
            CallWithMarkup(
                sentinel.chat_id,
                (
                    'You can get the value for a configuration key, '
                    'set it of change it if exists, or clear the key. '
                    'You can also cancel the config command at any time.'
                ),
                reply_markup_dict=self.action_markup_dict,
            ),
        )
        assert {'chat_id': 201, 'message_id': 202} == self.chat_data

    def test_get_handler(self):
        with self.assert_log(
            'Requesting key name to get its value.', logger,
        ):
            assert GET_VAR == get_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Tell me what key do you want to get.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )

    @patch.dict(f'{MODULE_PATH}.config', {}, True)
    def test_get_var_handler_missing(self):
        self.set_string_command('key')
        with self.assert_log('Key doesn\'t exists.', logger):
            assert ConversationHandler.END == get_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The key \'key\' doesn\'t exists.')
        assert {} == self.chat_data

    @patch.dict(f'{MODULE_PATH}.config', {'key': 'result'}, True)
    def test_get_var_handler_exists(self):
        self.set_string_command('key')
        with self.assert_log('Replying with result \'result\'.', logger):
            assert ConversationHandler.END == get_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The value for key \'key\' is \'result\'.')
        assert {} == self.chat_data

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_get_var_handler_invalid_key(self, _config):
        self.set_string_command('invalid-key')
        with self.assert_log('Key was invalid.', logger):
            assert ConversationHandler.END == get_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The key \'invalid-key\' is not a valid key.')
        assert {} == self.chat_data

    def test_set_handler(self):
        with self.assert_log(
            'Requesting key name to set its value.', logger,
        ):
            assert SET_VAR == set_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Tell me what key do you want to set.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )

    def test_set_var_handler_missing(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.set_string_command('key')
        with self.assert_log(
            'Requesting value to set the key.', logger,
        ):
            assert SET_VALUE == set_var_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Tell me what value do you want to put in the key \'key\'.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )
        assert {'chat_id': 1, 'message_id': 2, 'key': 'key'} == self.chat_data

    def test_set_var_handler_exists(self):
        fake_config = {'key': 'val'}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.set_string_command('key')
        with self.assert_log(
            'Requesting value to set the key.', logger,
        ):
            assert SET_VALUE == set_var_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Tell me what value do you want to put in the key \'key\'.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )
        assert {'chat_id': 1, 'message_id': 2, 'key': 'key'} == self.chat_data

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_set_var_handler_invalid_key(self, _config):
        self.set_string_command('invalid-key')
        with self.assert_log('Can\'t set invalid config key \'invalid-key\'.', logger):
            assert ConversationHandler.END == set_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The key \'invalid-key\' is not a valid key.')
        assert {} == self.chat_data

    def test_set_value_handler_set(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.chat_data['key'] = 'key'
        self.set_string_command('val')
        with self.assert_log(
            'Stored \'val\' in key \'key\'.', logger,
        ):
            assert ConversationHandler.END == set_value_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'I\'ll remember that.')
        assert {'key': 'val'} == fake_config
        assert {} == self.chat_data

    def test_del_handler(self):
        with self.assert_log(
            'Requesting key name to clear its value.', logger,
        ):
            assert DEL_VAR == del_handler(*self.update_and_context)
        self.assert_edit_call(
            CallWithMarkup(
                'Tell me what key do you want to clear.',
                1,
                2,
                reply_markup_dict=self.cancel_markup_dict,
            )
        )

    def test_del_var_handler_missing(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.set_string_command('key')
        with self.assert_log('Key doesn\'t exists.', logger):
            assert ConversationHandler.END == del_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The key \'key\' doesn\'t exists.')
        assert {} == fake_config

    def test_del_var_handler_exists(self):
        fake_config = {'key': 'val'}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.set_string_command('key')
        with self.assert_log(
            'Deleting config with key \'key\'.', logger,
        ):
            assert ConversationHandler.END == del_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'I\'ll forget that.')
        assert {} == fake_config

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_del_var_handler_invalid_key(self, _config):
        self.set_string_command('invalid-key')
        with self.assert_log('Key was invalid.', logger):
            assert ConversationHandler.END == del_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'The key \'invalid-key\' is not a valid key.')
        assert {} == self.chat_data

    def test_cancel_handler(self):
        self.chat_data.update(
            {'chat_id': 1, 'message_id': 2, 'key': 'key', 'some': 'content'}
        )
        with self.assert_log(
            'Abort config conversation.', logger,
        ):
            assert ConversationHandler.END == cancel_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_message_chat_text(1, 'Ok.')
        assert {'some': 'content'} == self.chat_data
