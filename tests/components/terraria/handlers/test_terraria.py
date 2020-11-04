from fjfnaranjobot.components.terraria.handlers.terraria import logger, terraria_handler

from ....base import BotHandlerTestCase


class TerrariaHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.user_is_friend()

    def test_terraria_handler_does_nothing(self):
        with self.assert_log_dispatch(
            "The 'terraria' command is not implemented.", logger
        ):
            terraria_handler(*self.update_and_context)
