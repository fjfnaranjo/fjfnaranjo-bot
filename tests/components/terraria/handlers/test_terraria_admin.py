from unittest.mock import sentinel

from fjfnaranjobot.auth import logger as auth_logger
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.components.terraria.handlers.terraria_admin import (
    terraria_admin_handler,
)

from ....base import (
    LOG_BOT_UNAUTHORIZED_HEAD,
    LOG_FRIEND_UNAUTHORIZED_HEAD,
    LOG_NO_USER_HEAD,
    LOG_USER_UNAUTHORIZED_HEAD,
    BotHandlerTestCase,
)


class TerrariaAdminHandlersTests(BotHandlerTestCase):
    def setUp(self):
        super().setUp()
        self.user_is_owner()

    def test_terraria_admin_handler_user_none(self):
        self.user_is_none()
        with self.assert_log_dispatch(LOG_NO_USER_HEAD, auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_terraria_admin_handler_unknown_unauthorized(self):
        self.user_is_unknown()
        with self.assert_log_dispatch(LOG_USER_UNAUTHORIZED_HEAD, auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_terraria_admin_handler_bot_unauthorized(self):
        self.user_is_bot()
        with self.assert_log_dispatch(LOG_BOT_UNAUTHORIZED_HEAD, auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)

    def test_terraria_admin_handler_friend_unauthorized(self):
        self.user_is_friend()
        with self.assert_log_dispatch(LOG_FRIEND_UNAUTHORIZED_HEAD, auth_logger):
            terraria_admin_handler(*self.update_and_context)
        self.assert_message_chat_text(sentinel.chat_id, SORRY_TEXT)
