from unittest import TestCase
from unittest.mock import patch, MagicMock

from telegram.ext import DispatcherHandlerStop
from pytest import raises

from fjfnaranjobot.components.config.use_cases import config_set, config_get


class ConfigModuleTests(TestCase):
    @patch('fjfnaranjobot.components.config.use_cases.set_key')
    def test_config_set(self, set_key):
        update = MagicMock()
        update.message.text = f'cmd key val'
        update.effective_user.is_bot = False
        update.effective_user.id = 99
        with raises(DispatcherHandlerStop):
            config_set(update, None)
        set_key.assert_called_once_with('key', 'val')
        update.message.reply_text.assert_called_once_with('ok')

    @patch('fjfnaranjobot.components.config.use_cases.get_key')
    def test_config_get_missing(self, get_key):
        update = MagicMock()
        update.message.text = f'cmd key'
        update.effective_user.is_bot = False
        update.effective_user.id = 99
        get_key.return_value = None
        with raises(DispatcherHandlerStop):
            config_get(update, None)
        get_key.assert_called_once_with('key')
        update.message.reply_text.assert_called_once()
        message_contents = update.message.reply_text.call_args[0][0]
        assert 'No value' in message_contents

    @patch('fjfnaranjobot.components.config.use_cases.get_key')
    def test_config_get_exists(self, get_key):
        update = MagicMock()
        update.message.text = f'cmd key'
        update.effective_user.is_bot = False
        update.effective_user.id = 99
        get_key.return_value = 'result'
        with raises(DispatcherHandlerStop):
            config_get(update, None)
        get_key.assert_called_once_with('key')
        update.message.reply_text.assert_called_once_with('result')
