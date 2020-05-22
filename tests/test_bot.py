from unittest.mock import MagicMock, patch

from fjfnaranjobot.bot import (
    Bot,
    BotJSONError,
    BotLibraryError,
    BotTokenError,
    EnvValueError,
    get_bot_data_dir,
)

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.bot'
BOT_DATA_DIR_DEFAULT = 'botdata'
BOT_DATA_DIR_TEST = '/bot/data/test'


class BotUtilsTests(BotTestCase):
    def test_get_bot_data_dir_default(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', None, ['BOT_DATA_DIR']
        ):
            assert get_bot_data_dir() == BOT_DATA_DIR_DEFAULT

    def test_get_bot_data_dir_env(self):
        with self._with_mocked_environ(
            f'{MODULE_PATH}.environ', {'BOT_DATA_DIR': BOT_DATA_DIR_TEST}
        ):
            assert get_bot_data_dir() == BOT_DATA_DIR_TEST


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
        Bot()
        tbot.assert_called_once_with('bt')
        dispatcher.assert_called_once_with(
            created_bot, None, workers=0, use_context=True
        )

    def test_process_request_salute(self, _dispatcher, _tbot):
        bot = Bot()
        assert 'I\'m' in bot.process_request('', None)

    def test_process_request_salute_root(self, _dispatcher, _tbot):
        bot = Bot()
        assert 'I\'m' in bot.process_request('/', None)

    def test_process_request_ping(self, _dispatcher, _tbot):
        bot = Bot()
        assert 'pong' == bot.process_request('/ping', None)

    def test_process_request_register_webhook(self, _dispatcher, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        bot = Bot()
        assert 'ok' == bot.process_request('/bwt/register_webhook', None)
        created_bot.set_webhook.assert_called_once_with(url='bwu/bwt')

    @patch(f'{MODULE_PATH}.open')
    def test_process_request_register_webhook_self(self, open_, _dispatcher, tbot):
        created_bot = MagicMock()
        tbot.return_value = created_bot
        opened_file = MagicMock()
        open_.return_value = opened_file
        bot = Bot()
        assert 'ok (self)' == bot.process_request('/bwt/register_webhook_self', None)
        open_.assert_called_once_with('/botcert/YOURPUBLIC.pem', 'rb')
        created_bot.set_webhook.assert_called_once_with(
            url='bwu/bwt', certificate=opened_file
        )

    def test_process_request_invalid_json(self, _dispatcher, _tbot):
        bot = Bot()
        with self.assertRaises(BotJSONError):
            bot.process_request('/bwt', '---')

    @patch(f'{MODULE_PATH}.Update')
    def test_process_request_dispatched_ok(self, update, dispatcher, _tbot):
        bot = Bot()
        parsed_update = MagicMock()
        update.de_json.return_value = parsed_update
        bot.process_request('/bwt', '{}')
        dispatcher.process_update(parsed_update)

    @patch(f'{MODULE_PATH}.Update')
    def test_process_request_dispatched_error(self, update, _dispatcher, _tbot):
        bot = Bot()
        update.de_json.side_effect = Exception
        with self.assertRaises(BotLibraryError):
            bot.process_request('/bwt', '{}')

    def test_other_urls(self, _tbot, _dispatcher):
        bot = Bot()
        with self.assertRaises(BotTokenError):
            bot.process_request('/other', None)


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
        bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock5')
    def test_component_with_ok_handlers_and_group(self, _dispatcher, _tbot):
        bot = Bot()
        assert 2 == bot.dispatcher.add_handler.call_count

    @patch(f'{MODULE_PATH}.BOT_COMPONENTS', 'component_mock6')
    def test_component_with_ok_handlers_and_invalid_group(self, _dispatcher, _tbot):
        with self.assertRaises(EnvValueError) as e:
            Bot()
        assert 'group' in str(e.exception)
