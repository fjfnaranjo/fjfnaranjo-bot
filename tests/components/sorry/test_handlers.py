from unittest.mock import patch

from fjfnaranjobot.components.sorry.handlers import sorry_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.sorry.handlers'


@patch(f'{MODULE_PATH}.sorry')
class SorryHandlersTests(BotHandlerTestCase):
    def test_friends_called(self, sorry):
        sorry_handler(self._update)
        assert sorry.called
