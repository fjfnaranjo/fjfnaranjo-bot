from logging import DEBUG
from unittest import TestCase
from unittest.mock import MagicMock, patch

from telegram.error import TelegramError

from fjfnaranjobot.bot import Bot, BotJSONError, BotTokenError, logger

MODULE_PATH = "fjfnaranjobot.bot"


@patch(f"{MODULE_PATH}.TBot")
@patch(f"{MODULE_PATH}.get_bot_components", return_value="")
@patch(f"{MODULE_PATH}.BOT_WEBHOOK_URL", "bwu")
@patch(f"{MODULE_PATH}.BOT_WEBHOOK_TOKEN", "bwt")
@patch(f"{MODULE_PATH}.BOT_WEBHOOK_CERT", "cert")
class BotTests(TestCase):
    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_bot_uses_tbot_and_dispatcher(self, dispatcher, _get_bot_components, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        with self.assertLogs(logger, DEBUG) as logs:
            Bot()
        tbot.assert_called_once_with("123456:btbtbt")
        dispatcher.assert_called_once_with(
            created_bot, None, workers=0, use_context=True
        )
        assert "Bot init done." in logs.output[-2]
        assert "Bot handlers registered." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Update")
    def test_bot_log_exceptions(self, update, _get_bot_components, _tbot):
        bot = Bot()
        parsed_update = TelegramError("msg")
        update.de_json.return_value = parsed_update
        with self.assertLogs(logger) as logs:
            bot.process_request("/bwt", "{}")
        assert "Error inside the framework raised by the dispatcher." in logs.output[0]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_process_request_salute(self, _dispatcher, _get_bot_components, _tbot):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == bot.process_request("", None)
        assert "Reply with salute." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_process_request_salute_root(self, _dispatcher, _get_bot_components, _tbot):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "I'm fjfnaranjo's bot." == bot.process_request("/", None)
        assert "Reply with salute." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_process_request_ping(self, _dispatcher, _get_bot_components, _tbot):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "pong" == bot.process_request("/ping", None)
        assert "Reply with pong." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_process_request_register_webhook(
        self, _dispatcher, _get_bot_components, tbot
    ):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok" == bot.process_request("/bwt/register_webhook", None)
        created_bot.set_webhook.assert_called_once_with(url="bwu/bwt")
        assert "Reply with ok to register_webhook." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    @patch(f"{MODULE_PATH}.open")
    def test_process_request_register_webhook_self(
        self, open_, _dispatcher, _get_bot_components, tbot
    ):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        opened_file = MagicMock()
        open_.return_value = opened_file
        bot = Bot()
        with self.assertLogs(logger) as logs:
            assert "ok (self)" == bot.process_request(
                "/bwt/register_webhook_self", None
            )
        open_.assert_called_once_with("cert", "rb")
        created_bot.set_webhook.assert_called_once_with(
            url="bwu/bwt", certificate=opened_file
        )
        assert "Reply with ok to register_webhook_self." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_process_request_invalid_json(
        self, _dispatcher, _get_bot_components, _tbot
    ):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotJSONError) as e:
                bot.process_request("/bwt", "---")
        assert "Sent content isn't JSON." == e.exception.args[0]
        assert "Received non-JSON request." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    @patch(f"{MODULE_PATH}.Update")
    def test_process_request_dispatched_ok(
        self, update, dispatcher, _get_bot_components, _tbot
    ):
        bot = Bot()
        parsed_update = MagicMock()
        update.de_json.return_value = parsed_update
        with self.assertLogs(logger, DEBUG) as logs:
            bot.process_request("/bwt", "{}")
        dispatcher.process_update(parsed_update)
        assert "Dispatch update to library." in logs.output[-1]

    @patch(f"{MODULE_PATH}.Dispatcher")
    def test_other_urls(self, _dispatcher, _get_bot_components, _tbot):
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


@patch(f"{MODULE_PATH}.TBot")
@patch(f"{MODULE_PATH}.Dispatcher")
@patch(
    f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.handlers.{}.info"
)
class ComponentLoaderHandlersTests(TestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_handlers(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_handlers(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert (
            "Invalid handlers definition for component 'component_mock3'."
            == e.exception.args[0]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_ok_handlers(self, _get_bot_components, _dispatcher, _tbot):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 6 == bot.dispatcher.add_handler.call_count
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
    def test_component_with_ok_conversation(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count
        assert (
            "Registered command 'cmdm51' with callback '<lambda>' "
            "for component 'component_mock5' and group number 0." in logs.output[-2]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock6")
    def test_component_with_invalid_handler(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid handler for component 'component_mock6'." == e.exception.args[0]


@patch(f"{MODULE_PATH}.TBot")
@patch(f"{MODULE_PATH}.Dispatcher")
@patch(f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.group.{}.info")
class ComponentLoaderGroupTests(TestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_group(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_group(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid group for component 'component_mock3'." == e.exception.args[0]

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_ok_handlers_and_no_group(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count
        assert (
            "Registered command 'cmdm41' with callback '<lambda>' "
            "for component 'component_mock4' and group number 0." in logs.output[-2]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock5")
    def test_component_with_ok_handlers_and_group(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count
        assert (
            "Registered command 'cmdm51' with callback '<lambda>' "
            "for component 'component_mock5' and group number 99." in logs.output[-2]
        )


@patch(f"{MODULE_PATH}.TBot")
@patch(f"{MODULE_PATH}.Dispatcher")
@patch(
    f"{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE", "tests.component_mocks.commands.{}.info"
)
class ComponentLoaderCommandsTests(TestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_commands(self, _get_bot_components, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_called_once()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_command(
        self, _get_bot_components, _dispatcher, _tbot
    ):
        with self.assertRaises(ValueError) as e:
            Bot()
        assert "Invalid command for component 'component_mock3'." == e.exception.args[0]

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_component(self, _get_bot_components, _dispatcher, _tbot):
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
