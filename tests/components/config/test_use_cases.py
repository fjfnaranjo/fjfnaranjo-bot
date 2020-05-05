from unittest.mock import patch


from fjfnaranjobot.components.config.use_cases import config_set, config_get
from tests.base import BotUseCaseTestCase


MODULE_PATH = 'fjfnaranjobot.components.config.use_cases'


class ConfigUseCasesTests(BotUseCaseTestCase):
    @patch(f'{MODULE_PATH}.set_key')
    def test_config_set(self, set_key):
        self._user_is_owner()
        self._set_msg('cmd key val')
        with self._raises_dispatcher_stop():
            config_set(self.update, None)
        set_key.assert_called_once_with('key', 'val')
        self.update.message.reply_text.assert_called_once_with('ok')

    @patch(f'{MODULE_PATH}.get_key')
    def test_config_get_missing(self, get_key):
        self._user_is_owner()
        self._set_msg('cmd key')
        get_key.return_value = None
        with self._raises_dispatcher_stop():
            config_get(self.update, None)
        get_key.assert_called_once_with('key')
        self.update.message.reply_text.assert_called_once()
        message_contents = self.update.message.reply_text.call_args[0][0]
        assert 'No value' in message_contents

    @patch(f'{MODULE_PATH}.get_key')
    def test_config_get_exists(self, get_key):
        self._user_is_owner()
        self._set_msg('cmd key')
        get_key.return_value = 'result'
        with self._raises_dispatcher_stop():
            config_get(self.update, None)
        get_key.assert_called_once_with('key')
        self.update.message.reply_text.assert_called_once_with('result')
