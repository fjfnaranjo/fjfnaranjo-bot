from logging import DEBUG
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch, sentinel

from fjfnaranjobot.bot import Bot, BotJSONError, BotTokenError, logger

MODULE_PATH = "fjfnaranjobot.bot"


class BaseBotTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self.application_patcher = patch(f"{MODULE_PATH}.Application")
        self.patched_application = self.application_patcher.start()
        self.builder = MagicMock()
        self.application = MagicMock()
        self.application.update_queue.put = AsyncMock()
        self.bot = MagicMock()
        self.bot.process_request = AsyncMock()
        self.bot.set_webhook = AsyncMock()
        self.application.bot = self.bot
        self.builder.build.return_value = self.application
        self.patched_application.builder.return_value = self.builder

    def tearDown(self):
        self.application_patcher.stop()
        super().tearDown()


@patch(f"{MODULE_PATH}.get_bot_components", return_value="")
class BotTests(BaseBotTestCase):
    def test_bot_uses_builder_and_register_exceptions(self, _get_bot_components):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        self.builder.token.assert_called_once_with("123456:btbtbt")
        self.builder.updater.assert_called_once_with(None)
        assert bot.application == self.application
        assert bot.bot == self.bot
        assert "DEBUG:app.fjfnaranjobot.bot:Bot init done." in logs.output
        bot.application.add_error_handler.assert_called_once_with(
            bot._log_error_from_context
        )
        assert "DEBUG:app.fjfnaranjobot.bot:Bot handlers registered." in logs.output

    @patch(f"{MODULE_PATH}.Update")
    @patch(f"{MODULE_PATH}.logger")
    def test_bot_logs_exceptions(self, logger, _update, _get_bot_components):
        bot = Bot()
        context = MagicMock()
        context.error = sentinel.error
        bot._log_error_from_context(None, context)
        logger.exception.assert_called_once_with(
            "Error inside the framework raised by the application.",
            exc_info=sentinel.error,
        )

    async def test_process_request_salute(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == await bot.process_request("", None)
        assert "Reply with salute." in logs.output[-1]

    async def test_process_request_salute_root(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == await bot.process_request("/", None)
        assert "Reply with salute." in logs.output[-1]

    async def test_process_request_ping(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "pong" == await bot.process_request("/ping", None)
        assert "Reply with pong." in logs.output[-1]

    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_URL", "bwu")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    async def test_process_request_register_webhook(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok" == await bot.process_request("/bwt/register_webhook", None)
        self.bot.set_webhook.assert_called_once_with(
            url="bwu/bwt", drop_pending_updates=True
        )
        assert "Reply with ok to register_webhook." in logs.output[-1]

    @patch(f"{MODULE_PATH}.open")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_URL", "bwu")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_CERT", "cert")
    async def test_process_request_register_webhook_self(
        self, open_, _get_bot_components
    ):
        opened_file = MagicMock()
        open_.return_value = opened_file
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok (self)" == await bot.process_request(
                "/bwt/register_webhook_self", None
            )
        open_.assert_called_once_with("cert", "rb")
        self.bot.set_webhook.assert_called_once_with(
            url="bwu/bwt", certificate=opened_file, drop_pending_updates=True
        )
        assert "Reply with ok to register_webhook_self." in logs.output[-1]

    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    async def test_process_request_invalid_json(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotJSONError) as e:
                await bot.process_request("/bwt", "---")
        assert "Sent content isn't JSON." == e.exception.args[0]
        assert "Received non-JSON request." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Update")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    async def test_process_request_dispatched_ok(self, update, _get_bot_components):
        bot = Bot()
        parsed_update = MagicMock()
        update.de_json.return_value = parsed_update
        with self.assertLogs(logger, DEBUG) as logs:
            await bot.process_request("/bwt", "{}")
        self.application.update_queue.put.assert_called_once_with(parsed_update)
        assert "Dispatch update to library." in logs.output[-1]

    async def test_other_urls(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotTokenError) as e:
                await bot.process_request("/other", None)
        assert (
            "Path '/other' (cropped to 10 chars) not preceded by token and not handled by bot."
            in e.exception.args[0]
        )
        assert (
            "Path '/other' (cropped to 10 chars) not preceded by token and not handled by bot."
            in logs.output[0]
        )
