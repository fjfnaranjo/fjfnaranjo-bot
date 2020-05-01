from unittest import TestCase
from unittest.mock import patch, MagicMock


from fjfnaranjobot.components.config.use_cases import config_set, config_get


class ConfigTests(TestCase):
    @patch('fjfnaranjobot.components.config.use_cases.set_key')
    def test_config_set(self, set_key):
        update = MagicMock()
        update.message.text = f'cmd key val'
        config_set(update, None)
        set_key.assert_called_once_with('key', 'val')
        update.message.reply_text.assert_called_once_with('ok')

    @patch('fjfnaranjobot.components.config.use_cases.get_key')
    def test_config_get(self, get_key):
        update = MagicMock()
        update.message.text = f'cmd key'
        config_get(update, None)
        get_key.assert_called_once_with('key')
