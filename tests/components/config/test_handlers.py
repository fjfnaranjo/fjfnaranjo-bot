from unittest.mock import patch

from fjfnaranjobot.components.config.handlers import (
    config_del_handler,
    config_get_handler,
    config_set_handler,
    logger,
)

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.config.handlers'


class ConfigHandlersTests(BotHandlerTestCase):
    def setUp(self):
        BotHandlerTestCase.setUp(self)
        self._user_is_owner()

    def test_config_set(self):
        fake_config = {}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_update_message_text('config_set', ['key', 'val'])
        with self._assert_reply_log_dispatch(
            'I\'ll remember that.',
            'Stored \'val\' (cropped to 10 chars) with key \'key\'.',
            logger,
        ):
            config_set_handler(self._update, None)
        assert 1 == len(fake_config)
        assert 'val' == fake_config['key']

    @patch.dict(f'{MODULE_PATH}.config', {}, True)
    def test_config_get_missing(self):
        self._set_update_message_text('config_get', ['key'])
        with self._assert_reply_log_dispatch(
            'No value for key \'key\'.',
            'Replying with \'no value\' message for key \'key\'.',
            logger,
        ):
            config_get_handler(self._update, None)

    @patch.dict(f'{MODULE_PATH}.config', {'key': 'result'}, True)
    def test_config_get_exists(self):
        self._set_update_message_text('config_get', ['key'])
        with self._assert_reply_log_dispatch(
            'result',
            'Replying with \'result\' (cropped to 10 chars) for key \'key\'.',
            logger,
        ):
            config_get_handler(self._update, None)

    def test_config_del_missing(self):
        fake_config = {}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_update_message_text('config_del', ['key'])
        with self._assert_reply_log_dispatch(
            'I don\'t know anything about \'key\'.',
            'Tried to delete config with key \'key\' but it didn\'t exists.',
            logger,
        ):
            config_del_handler(self._update, None)
        assert 0 == len(fake_config)

    def test_config_del_exists(self):
        fake_config = {'key': 'val'}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_update_message_text('config_del', ['key'])
        with self._assert_reply_log_dispatch(
            'I\'ll forget that.', 'Deleting config with key \'key\'.', logger,
        ):
            config_del_handler(self._update, None)
        assert 0 == len(fake_config)
