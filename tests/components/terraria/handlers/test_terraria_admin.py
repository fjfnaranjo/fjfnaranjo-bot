from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.components.terraria.handlers.terraria_admin import (
    terraria_admin_handler,
)

from ....base import BotHandlerTestCase


class TerrariaAdminHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.user_is_owner()

    def test_terraria_admin_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assert_log_dispatch('Message received with no user', auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_reply(SORRY_TEXT)

    def test_terraria_admin_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assert_log_dispatch('Message received from bot', auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_reply(SORRY_TEXT)

    def test_terraria_admin_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assert_log_dispatch('User f with id 21', auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_reply(SORRY_TEXT)
