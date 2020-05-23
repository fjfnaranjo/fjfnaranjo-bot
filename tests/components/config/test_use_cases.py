from unittest.mock import patch

from fjfnaranjobot.components.config.use_cases import (
    config_del,
    config_get,
    config_set,
    logger,
)

from ...base import BotUseCaseTestCase

MODULE_PATH = 'fjfnaranjobot.components.config.use_cases'


class ConfigUseCasesTests(BotUseCaseTestCase):
    def test_config_set(self):
        fake_config = {}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_msg('cmd key val')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_set(self._update, None)
        assert 1 == len(fake_config)
        assert 'val' == fake_config['key']
        self._update.message.reply_text.assert_called_once_with('I\'ll remember that.')
        assert (
            'Stored \'val\' (cropped to 10 chars) with key \'key\'.' in logs.output[0]
        )

    @patch.dict(f'{MODULE_PATH}.config', {}, True)
    def test_config_get_missing(self):
        self._set_msg('cmd key')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_get(self._update, None)
        self._update.message.reply_text.assert_called_once()
        message_contents = self._update.message.reply_text.call_args[0][0]
        assert 'No value for key \'key\'.' == message_contents
        assert 'Replying with \'no value\' message for key \'key\'.' in logs.output[0]

    @patch.dict(f'{MODULE_PATH}.config', {'key': 'result'}, True)
    def test_config_get_exists(self):
        self._set_msg('cmd key')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_get(self._update, None)
        self._update.message.reply_text.assert_called_once_with('result')
        assert (
            'Replying with \'result\' (cropped to 10 chars) for key \'key\'.'
            in logs.output[0]
        )

    def test_config_del_missing(self):
        fake_config = {}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_msg('cmd key')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_del(self._update, None)
        assert 0 == len(fake_config)
        self._update.message.reply_text.assert_called_once_with(
            'I don\'t know anything about \'key\'.'
        )
        assert (
            'Tried to delete config with key \'key\' but it didn\'t exists.'
            in logs.output[0]
        )

    def test_config_del_exists(self):
        fake_config = {'key': 'val'}
        patch(f'{MODULE_PATH}.config', fake_config).start()
        self._set_msg('cmd key')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_del(self._update, None)
        assert 0 == len(fake_config)
        self._update.message.reply_text.assert_called_once_with('I\'ll forget that.')
        assert 'Deleting config with key \'key\'.' in logs.output[0]
