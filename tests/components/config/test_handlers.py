from unittest.mock import MagicMock, patch

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
        self._user_is_owner()

    def test_config_handler(self):
        with self._assert_reply_log(
            (
                'If you want to get the value for a configuration key, use /config_get . '
                'If you want to set the value, /config_set . '
                'If you want to clear it, /config_del . '
                'If you want to do something else, /config_cancel .'
            ),
            'Entering config conversation.',
            logger,
        ):
            assert GET_SET_OR_DEL == config_handler(self._update, self._context)

    def test_get_handler(self):
        with self._assert_reply_log(
            'Tell me what key do you want to get.',
            'Requesting key name to get its value.',
            logger,
        ):
            assert GET_VAR == get_handler(self._update, self._context)

    @patch.dict(f'{MODULE_PATH}.config', {}, True)
    def test_get_var_handler_missing(self):
        self._set_string_command('key')
        with self._assert_reply_log(
            'No value for key \'key\'.',
            'Replying with \'no value\' message for key \'key\'.',
            logger,
        ):
            assert ConversationHandler.END == get_var_handler(
                self._update, self._context
            )

    @patch.dict(f'{MODULE_PATH}.config', {'key': 'result'}, True)
    def test_get_var_handler_exists(self):
        self._set_string_command('key')
        with self._assert_reply_log(
            'result',
            'Replying with \'result\' (cropped to 10 chars) for key \'key\'.',
            logger,
        ):
            assert ConversationHandler.END == get_var_handler(
                self._update, self._context
            )

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_get_var_handler_invalid_key(self, _config):
        self._set_string_command('invalid-key')
        with self.assertRaises(ValueError) as e:
            get_var_handler(self._update, self._context)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]

    def test_set_handler(self):
        with self._assert_reply_log(
            'Tell me what key do you want to set.',
            'Requesting key name to set its value.',
            logger,
        ):
            assert SET_VAR == set_handler(self._update, self._context)

    def test_set_var_handler(self):
        self._set_string_command('key')
        self._set_user_data({})
        with self._assert_reply_log(
            'Tell me what value do you want to put in the key \'key\'.',
            'Requesting key name to set its value.',
            logger,
        ):
            assert SET_VALUE == set_var_handler(self._update, self._context)
        assert 'key' == self._context.user_data['key']

    def test_set_value_handler_set(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self._set_user_data({'key': 'key'})
        self._set_string_command('val')
        with self._assert_reply_log(
            'I\'ll remember that.',
            'Stored \'val\' (cropped to 10 chars) with key \'key\'.',
            logger,
        ):
            assert ConversationHandler.END == set_value_handler(
                self._update, self._context
            )
        assert 1 == len(fake_config)
        assert 'val' == fake_config['key']
        assert 0 == len(self._context.user_data)

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_set_value_handler_invalid_key(self, _config):
        self._set_user_data({'key': 'invalid-key'})
        self._set_string_command('val')
        with self.assertRaises(ValueError) as e:
            set_value_handler(self._update, self._context)
        assert 0 == len(self._context.user_data)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]
        assert 0 == len(self._context.user_data)

    def test_del_handler(self):
        with self._assert_reply_log(
            'Tell me what key do you want to clear.',
            'Requesting key name to clear its value.',
            logger,
        ):
            assert DEL_VAR == del_handler(self._update, self._context)

    def test_del_var_handler_missing(self):
        fake_config = {}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self._set_string_command('key')
        with self._assert_reply_log(
            'I don\'t know anything about \'key\'.',
            'Tried to delete config with key \'key\' but it didn\'t exists.',
            logger,
        ):
            assert ConversationHandler.END == del_var_handler(
                self._update, self._context
            )
        assert 0 == len(fake_config)

    def test_config_del_exists(self):
        fake_config = {'key': 'val'}
        patcher = patch(f'{MODULE_PATH}.config', fake_config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self._set_string_command('key')
        with self._assert_reply_log(
            'I\'ll forget that.', 'Deleting config with key \'key\'.', logger,
        ):
            assert ConversationHandler.END == del_var_handler(
                self._update, self._context
            )
        assert 0 == len(fake_config)

    @patch(f'{MODULE_PATH}.config.__setitem__', side_effect=ValueError)
    def test_del_var_handler_invalid_key(self, _config):
        self._set_string_command('invalid-key')
        with self.assertRaises(ValueError) as e:
            del_var_handler(self._update, self._context)
        assert 'No valid value for key invalid-key.' in e.exception.args[0]

    def test_cancel_handler(self):
        self._set_user_data({'key': 'invalid-key'})
        with self._assert_reply_log(
            'Ok.', 'Abort config conversation.', logger,
        ):
            assert ConversationHandler.END == cancel_handler(
                self._update, self._context
            )
        assert 0 == len(self._context.user_data)
