from logging import DEBUG
from unittest.mock import MagicMock, patch

from fjfnaranjobot.bot import Bot, BotJSONError, BotLibraryError, BotTokenError, logger
from fjfnaranjobot.common import EnvValueError

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.bot'


@patch(f'{MODULE_PATH}.TBot')
@patch(f'{MODULE_PATH}.Dispatcher')
@patch(f'{MODULE_PATH}.BOT_TOKEN', 'bt')
@patch(f'{MODULE_PATH}.BOT_WEBHOOK_URL', 'bwu')
@patch(f'{MODULE_PATH}.BOT_WEBHOOK_TOKEN', 'bwt')
@patch(f'{MODULE_PATH}.BOT_COMPONENTS', '')
class BotTests(BotTestCase):
    def test_bot_uses_tbot_and_dispatcher(self, dispatcher, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        with self.assertLogs(logger, DEBUG) as logs:
            Bot()
        tbot.assert_called_once_with('bt')
        dispatcher.assert_called_once_with(
            created_bot, None, workers=0, use_context=True
        )
        assert 'Bot init' in logs.output[-2]
        assert 'Bot handlers registered' in logs.output[-1]

    def test_process_request_salute(self, _dispatcher, _tbot):
        bot = Bot()
        with self.assertLogs(logger, DEBUG) as logs:
            assert 'I\'m' in bot.process_request('', None)
        assert 'salute' in logs.output[-1]

    def test_process_request_salute_root(self, _dispatcher, _tbot):
        bot = Bot()
        with self.assertLogs(logger, DEBUG) as logs:
            assert 'I\'m' in bot.process_request('/', None)
        assert 'salute' in logs.output[-1]

    def test_process_request_ping(self, _dispatcher, _tbot):
        bot = Bot()
        with self.assertLogs(logger, DEBUG) as logs:
            assert 'pong' == bot.process_request('/ping', None)
        assert 'pong' in logs.output[-1]

    def test_process_request_register_webhook(self, _dispatcher, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        bot = Bot()
        with self.assertLogs(logger, DEBUG) as logs:
            assert 'ok' == bot.process_request('/bwt/register_webhook', None)
        created_bot.set_webhook.assert_called_once_with(url='bwu/bwt')
        assert 'ok' in logs.output[-1]
        assert 'register_webhook.' in logs.output[-1]

    @patch(f'{MODULE_PATH}.open')
    def test_process_request_register_webhook_self(self, open_, _dispatcher, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        opened_file = MagicMock()
        open_.return_value = opened_file
        bot = Bot()
        with self.assertLogs(logger, DEBUG) as logs:
            assert 'ok (self)' == bot.process_request(
                '/bwt/register_webhook_self', None
            )
        open_.assert_called_once_with('/botcert/YOURPUBLIC.pem', 'rb')
        created_bot.set_webhook.assert_called_once_with(
            url='bwu/bwt', certificate=opened_file
        )
        assert 'ok' in logs.output[-1]
        assert 'register_webhook_self.' in logs.output[-1]

    def test_process_request_invalid_json(self, _dispatcher, _tbot):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotJSONError):
                bot.process_request('/bwt', '---')
        assert 'non-JSON' in logs.output[-1]

    @patch(f'{MODULE_PATH}.Update')
    def test_process_request_dispatched_ok(self, update, dispatcher, _tbot):
        bot = Bot()
        parsed_update = MagicMock()
        update.de_json.return_value = parsed_update
        with self.assertLogs(logger, DEBUG) as logs:
            bot.process_request('/bwt', '{}')
        dispatcher.process_update(parsed_update)
        assert 'Dispatch update to' in logs.output[-1]

    @patch(f'{MODULE_PATH}.Update')
    def test_process_request_dispatched_error(self, update, _dispatcher, _tbot):
        bot = Bot()
        update.de_json.side_effect = Exception
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotLibraryError):
                bot.process_request('/bwt', '{}')
        assert 'Dispatcher raised an error' in logs.output[-1]

    def test_other_urls(self, _tbot, _dispatcher):
        bot = Bot()
        with self.assertLogs(logger) as logs:
            with self.assertRaises(BotTokenError):
                bot.process_request('/other', None)
        assert 'Uknown URL path' in logs.output[0]


@patch(f'{MODULE_PATH}.TBot')
@patch(f'{MODULE_PATH}.Dispatcher')
@patch(f'{MODULE_PATH}.BOT_WEBHOOK_URL', 'bwu')
@patch(f'{MODULE_PATH}.BOT_WEBHOOK_TOKEN', 'bwt')
@patch(f'{MODULE_PATH}._BOT_COMPONENTS_TEMPLATE', 'tests.component_mocks.{}.handlers')
class BotComponentLoaderTests(BotTestCase):
    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', '')
    def test_no_components(self, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_not_called()

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock1')
    def test_component_without_handlers(self, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_not_called()

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock2')
    def test_component_with_empty_handlers(self, _dispatcher, _tbot):
        bot = Bot()
        bot.dispatcher.add_handler.assert_not_called()

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock3')
    def test_component_with_invalid_handlers(self, _dispatcher, _tbot):
        with self.assertRaises(EnvValueError) as e:
            Bot()
        assert 'handler' in str(e.exception)

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock4')
    def test_component_with_ok_handlers_and_no_group(self, _dispatcher, _tbot):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count
        assert 'Registered' in logs.output[-3]
        assert 'Registered' in logs.output[-2]

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock5')
    def test_component_with_ok_handlers_and_group(self, _dispatcher, _tbot):
        with self.assertLogs(logger, DEBUG) as logs:
            bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count
        assert 'Registered' in logs.output[-3]
        assert 'Registered' in logs.output[-2]

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock6')
    def test_component_with_ok_handlers_and_invalid_group(self, _dispatcher, _tbot):
        with self.assertRaises(EnvValueError) as e:
            Bot()
        assert 'group' in str(e.exception)
