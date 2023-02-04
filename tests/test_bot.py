from logging import DEBUG
from unittest import TestCase
from unittest.mock import MagicMock, patch, sentinel

from telegram.error import TelegramError

from fjfnaranjobot.bot import Bot, BotJSONError, BotTokenError, logger

MODULE_PATH = "fjfnaranjobot.bot"


class BaseBotTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.application_patcher = patch(f"{MODULE_PATH}.Application")
        self.patched_application = self.application_patcher.start()
        self.builder = MagicMock()
        self.application = MagicMock()
        self.bot = MagicMock()
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
        assert bot.application == self.application
        assert bot.bot == self.bot
        assert "Bot init done." in logs.output[-2]
        bot.application.add_error_handler.assert_called_once_with(
            bot._log_error_from_context
        )
        assert "Bot handlers registered." in logs.output[-1]

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

    def test_process_request_salute(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == bot.process_request("", None)
        assert "Reply with salute." in logs.output[-1]

    def test_process_request_salute_root(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == bot.process_request("/", None)
        assert "Reply with salute." in logs.output[-1]

    def test_process_request_ping(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "pong" == bot.process_request("/ping", None)
        assert "Reply with pong." in logs.output[-1]

    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_URL", "bwu")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    def test_process_request_register_webhook(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok" == bot.process_request("/bwt/register_webhook", None)
        self.bot.set_webhook.assert_called_once_with(
            url="bwu/bwt", drop_pending_updates=True
        )
        assert "Reply with ok to register_webhook." in logs.output[-1]

    @patch(f"{MODULE_PATH}.open")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_URL", "bwu")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_CERT", "cert")
    def test_process_request_register_webhook_self(self, open_, _get_bot_components):
        opened_file = MagicMock()
        open_.return_value = opened_file
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok (self)" == bot.process_request(
                "/bwt/register_webhook_self", None
            )
        open_.assert_called_once_with("cert", "rb")
        self.bot.set_webhook.assert_called_once_with(
            url="bwu/bwt", certificate=opened_file, drop_pending_updates=True
        )
        assert "Reply with ok to register_webhook_self." in logs.output[-1]

    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    def test_process_request_invalid_json(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotJSONError) as e:
                bot.process_request("/bwt", "---")
        assert "Sent content isn't JSON." == e.exception.args[0]
        assert "Received non-JSON request." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Update")
    @patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
    def test_process_request_dispatched_ok(self, update, _get_bot_components):
        bot = Bot()
        parsed_update = MagicMock()
        update.de_json.return_value = parsed_update
        with self.assertLogs(logger, DEBUG) as logs:
            bot.process_request("/bwt", "{}")
        self.application.process_update.assert_called_once_with(parsed_update)
        assert "Dispatch update to library." in logs.output[-1]

    def test_other_urls(self, _get_bot_components):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotTokenError) as e:
                bot.process_request("/other", None)
        assert (
            "Path '/other' (cropped to 10 chars) not preceded by token and not handled by bot."
            in e.exception.args[0]
        )
        assert (
            "Path '/other' (cropped to 10 chars) not preceded by token and not handled by bot."
            in logs.output[0]
        )


@patch(
    f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.handlers.{}.info"
)
class ComponentLoaderHandlersTests(BaseBotTestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_handlers(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_handlers(self, _get_bot_components):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert (
            "Invalid handlers definition for component 'component_mock3'."
            == e.exception.args[0]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_ok_handlers(self, _get_bot_components):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 5 == bot.application.add_handler.call_count
        assert (
            "Registered command 'cmdm41' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-6]
        )
        assert (
            "Registered command 'cmdm42' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-5]
        )
        assert (
            "Registered command 'cmdm43' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-4]
        )
        assert (
            "Registered command '<message>' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-3]
        )
        assert (
            "Registered command '<unknown command>' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-2]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock5")
    def test_component_with_ok_conversation(self, _get_bot_components):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 1 == bot.application.add_handler.call_count
        assert (
            "Registered command 'cmdm51' with callback '<lambda>' "
            "for component 'component_mock5' and group number 0." in logs.output[-2]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock6")
    def test_component_with_invalid_handler(self, _get_bot_components):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid handler for component 'component_mock6'." == e.exception.args[0]


@patch(f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.group.{}.info")
class ComponentLoaderGroupTests(BaseBotTestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_group(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_group(self, _get_bot_components):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid group for component 'component_mock3'." == e.exception.args[0]

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_ok_handlers_and_no_group(self, _get_bot_components):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 1 == bot.application.add_handler.call_count
        assert (
            "Registered command 'cmdm41' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-2]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock5")
    def test_component_with_ok_handlers_and_group(self, _get_bot_components):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 1 == bot.application.add_handler.call_count
        assert (
            "Registered command 'cmdm51' with callback '<lambda>' "
            "for component 'component_mock5' and group number 99." in logs.output[-2]
        )


@patch(
    f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.commands.{}.info"
)
class ComponentLoaderCommandsTests(BaseBotTestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_commands(self, _get_bot_components):
        bot = Bot()
        bot.application.add_handler.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_command(self, _get_bot_components):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid command for component 'component_mock3'." == e.exception.args[0]

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_component(self, _get_bot_components):
        command_list_patcher = patch(f"{MODULE_PATH}.command_list", [])
        command_list_mock = command_list_patcher.start()
        self.addCleanup(command_list_patcher.stop)
        Bot()
        assert 3 == len(command_list_mock)
        assert "desc1" == command_list_mock[0].description
        assert "only_prod" == command_list_mock[0].prod_command
        assert None == command_list_mock[0].dev_command
        assert "desc2" == command_list_mock[1].description
        assert None == command_list_mock[1].prod_command
        assert "only_dev" == command_list_mock[1].dev_command
        assert "desc3" == command_list_mock[2].description
        assert "both_prod_and_dev" == command_list_mock[2].prod_command
        assert "both_prod_and_dev" == command_list_mock[2].dev_command
