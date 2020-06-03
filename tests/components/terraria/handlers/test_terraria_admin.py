from fjfnaranjobot.components.terraria.info import logger, terraria_admin_handler

from ....base import BotHandlerTestCase


class TerrariaAdminHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.user_is_owner()

    def test_terraria_admin_handler_does_nothing(self):
        with self.assert_log_dispatch(
            'The terraria admin command is not implemented.', logger
        ):
            terraria_admin_handler(*self.update_and_context)
