from fjfnaranjobot.components.terraria.info import (
    logger,
    terraria_admin_handler,
    terraria_handler,
)

from ...base import BotHandlerTestCase


class TerrariaHandlersTests(BotHandlerTestCase):
    def setUp(self, *args, **kwargs):
        BotHandlerTestCase.setUp(self, *args, **kwargs)
        self.user_is_owner()

    def test_terraria_admin_handler_does_nothing(self):
        with self.assert_log_dispatch(
            'The terraria admin command is not implemented.', logger
        ):
            terraria_admin_handler(*self.update_and_context)

    def test_terraria_handler_does_nothing(self):
        with self.assert_log_dispatch(
            'The terraria command is not implemented.', logger
        ):
            terraria_handler(*self.update_and_context)
