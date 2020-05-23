from unittest.mock import patch

from fjfnaranjobot.components.config.use_cases import config_get, config_set, logger

from ...base import BotUseCaseTestCase

MODULE_PATH = 'fjfnaranjobot.components.config.use_cases'


class ConfigUseCasesTests(BotUseCaseTestCase):
    @patch(f'{MODULE_PATH}.set_config')
    def test_config_set(self, set_config):
        self._set_msg('cmd key val')
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_set(self._update, None)
        set_config.assert_called_once_with('key', 'val')
        self._update.message.reply_text.assert_called_once_with('I\'ll remember that.')
        assert (
            'Stored \'val\' (cropped to 10 chars) with key \'key\'.' in logs.output[0]
        )

    @patch(f'{MODULE_PATH}.get_config')
    def test_config_get_missing(self, get_config):
        self._set_msg('cmd key')
        get_config.side_effect = KeyError()
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_get(self._update, None)
        get_config.assert_called_once_with('key')
        self._update.message.reply_text.assert_called_once()
        message_contents = self._update.message.reply_text.call_args[0][0]
        assert 'No value for key \'key\'.' in message_contents
        assert 'Replying with \'no value\' message for key \'key\'.' in logs.output[0]

    @patch(f'{MODULE_PATH}.get_config')
    def test_config_get_exists(self, get_config):
        self._set_msg('cmd key')
        get_config.return_value = 'result'
        with self.assertLogs(logger) as logs:
            with self._raises_dispatcher_stop():
                config_get(self._update, None)
        get_config.assert_called_once_with('key')
        self._update.message.reply_text.assert_called_once_with('result')
        assert (
            'Replying with \'result\' (cropped to 10 chars) for key \'key\'.'
            in logs.output[0]
        )
