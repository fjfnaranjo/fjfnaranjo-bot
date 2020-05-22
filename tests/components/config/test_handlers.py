from unittest.mock import patch

from fjfnaranjobot.components.config.handlers import (
    config_get_handler,
    config_set_handler,
)

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.config.handlers'


@patch(f'{MODULE_PATH}.config_get')
@patch(f'{MODULE_PATH}.config_set')
class ConfigHandlersTests(BotHandlerTestCase):
    def test_config_get_called(self, _config_set, config_get):
        self._user_is_owner()
        config_get_handler(self._update)
        assert config_get.called

    def test_config_set_called(self, config_set, _config_get):
        self._user_is_owner()
        config_set_handler(self._update)
        assert config_set.called
