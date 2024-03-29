from unittest.mock import patch

from fjfnaranjobot.components.start.info import logger, start_handler

from ...base import UNKNOWN_USER, BotHandlerTestCase

MODULE_PATH = "fjfnaranjobot.components.start.info"


@patch(f"{MODULE_PATH}.get_bot_owner_name", return_value="test")
class StartHandlersTests(BotHandlerTestCase):
    async def test_start_handler_processor(self, _get_bot_owner_name):
        with self.assert_log_dispatch(
            f"Greeting a new user with id {UNKNOWN_USER.id}.", logger
        ):
            await start_handler(*self.update_and_context)
        self.assert_reply_text(
            "Welcome. I'm test's bot. How can I help you?",
        )
