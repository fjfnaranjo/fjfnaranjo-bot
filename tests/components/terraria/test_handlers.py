from fjfnaranjobot.components.terraria.handlers import logger, terraria_handler

from ...base import BotHandlerTestCase

MODULE_PATH = 'fjfnaranjobot.components.terraria.handlers'


class TerrariaHandlersTests(BotHandlerTestCase):
    def setUp(self, *args, **kwargs):
        BotHandlerTestCase.setUp(self, *args, **kwargs)
        self.user_is_owner()

    def test_terraria_handler_does_nothing(self):
        with self.assert_log_dispatch(
            'The terraria command is not implemented.', logger
        ):
            terraria_handler(*self.update_and_context)
