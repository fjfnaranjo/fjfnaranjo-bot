from unittest.mock import patch

from telegram.ext.conversationhandler import ConversationHandler

from fjfnaranjobot.components.config.handlers import (
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

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.config.handlers'


class ConfigHandlersTests(BotHandlerTestCase):
    def setUp(self):
        BotHandlerTestCase.setUp(self)
        self.user_data = {'message_ids': (1, 2)}
        self.user_is_owner()

    def test_config_handler(self):
        self.user_data = {}
        with self.assert_log('Entering config conversation.', logger):
            assert GET_SET_OR_DEL == config_handler(*self.update_and_context)
        self.assert_reply(
            (
                'If you want to get the value for a configuration key, use /config_get . '
                'If you want to set the value, /config_set . '
                'If you want to clear it, /config_del . '
                'If you want to do something else, /config_cancel .'
            )
        )
        assert {
            'message_ids': (
                self.message_reply_text.chat.id,
                self.message_reply_text.message_id,
            )
        } == self.user_data

    def test_get_handler(self):
        with self.assert_log(
            'Requesting key name to get its value.', logger,
        ):
            assert GET_VAR == get_handler(*self.update_and_context)
        self.assert_edit(
            'Tell me what key do you want to get. '
            'If you want to do something else, /config_cancel .',
            1,
            2,
        )

    @patch.dict(f'{MODULE_PATH}.config', {}, True)
    def test_get_var_handler_missing(self):
        self.set_string_command('key')
        with self.assert_log(
            'Replying with \'no value\' message for key \'key\'.', logger,
        ):
            assert ConversationHandler.END == get_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_reply('No value for key \'key\'.')
        assert {} == self.user_data

    @patch.dict(f'{MODULE_PATH}.config', {'key': 'result'}, True)
    def test_get_var_handler_exists(self):
        self.set_string_command('key')
        with self.assert_log(
            'Replying with \'result\' (cropped to 10 chars) for key \'key\'.', logger
        ):
            assert ConversationHandler.END == get_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_reply('The value for key \'key\' is \'result\'.')
        assert {} == self.user_data

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_get_var_handler_invalid_key(self, _config):
        self.set_string_command('invalid-key')
        with self.assertRaises(ValueError) as e:
            get_var_handler(*self.update_and_context)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]

    def test_set_handler(self):
        with self.assert_log(
            'Requesting key name to set its value.', logger,
        ):
            assert SET_VAR == set_handler(*self.update_and_context)
        self.assert_edit(
            'Tell me what key do you want to set. '
            'If you want to do something else, /config_cancel .',
            1,
            2,
        )

    def test_set_var_handler(self):
        self.set_string_command('key')
        with self.assert_log(
            'Requesting value to set the key.', logger,
        ):
            assert SET_VALUE == set_var_handler(*self.update_and_context)
        self.assert_edit(
            'Tell me what value do you want to put in the key \'key\'. '
            'If you want to do something else, /config_cancel .',
            1,
            2,
        )
        assert {'message_ids': (1, 2), 'key': 'key'} == self.user_data

    def test_set_value_handler_set(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.user_data['key'] = 'key'
        self.set_string_command('val')
        with self.assert_log(
            'Stored \'val\' (cropped to 10 chars) in key \'key\'.', logger,
        ):
            assert ConversationHandler.END == set_value_handler(
                *self.update_and_context
            )
        self.assert_delete(1, 2)
        self.assert_reply('I\'ll remember that.')
        assert {'key': 'val'} == fake_config
        assert {} == self.user_data

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_set_value_handler_invalid_key(self, _config):
        self.user_data['key'] = 'invalid-key'
        self.set_string_command('val')
        with self.assertRaises(ValueError) as e:
            set_value_handler(*self.update_and_context)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]

    def test_del_handler(self):
        with self.assert_log(
            'Requesting key name to clear its value.', logger,
        ):
            assert DEL_VAR == del_handler(*self.update_and_context)
        self.assert_edit(
            'Tell me what key do you want to clear. '
            'If you want to do something else, /config_cancel .',
            1,
            2,
        )

    def test_del_var_handler_missing(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.set_string_command('key')
        with self.assert_log(
            'Tried to delete config with key \'key\' but it didn\'t exists.', logger,
        ):
            assert ConversationHandler.END == del_var_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        self.assert_reply('I don\'t know anything about \'key\'.')
        assert {} == fake_config

    def test_config_del_exists(self):
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
        self.assert_reply('I\'ll forget that.')
        assert {} == fake_config

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_del_var_handler_invalid_key(self, _config):
        self.set_string_command('invalid-key')
        with self.assertRaises(ValueError) as e:
            del_var_handler(*self.update_and_context)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]

    def test_cancel_handler(self):
        self.user_data.update({'key': 'key', 'some': 'content'})
        with self.assert_log(
            'Abort config conversation.', logger,
        ):
            assert ConversationHandler.END == cancel_handler(*self.update_and_context)
        self.assert_delete(1, 2)
        assert {'some': 'content'} == self.user_data
