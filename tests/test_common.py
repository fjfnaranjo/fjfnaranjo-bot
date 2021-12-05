from unittest import TestCase
from unittest.mock import MagicMock, call, patch, sentinel

from fjfnaranjobot.common import (
    Command,
    ScheduleEntry,
    User,
    get_bot_components,
    get_bot_owner_name,
    inline_handler,
    quote_value_for_log,
)

from .base import MockedEnvironTestCase

MODULE_PATH = "fjfnaranjobot.common"

BOT_OWNER_NAME_DEFAULT = "fjfnaranjo"
BOT_OWNER_NAME_TEST = "owner"

BOT_COMPONENTS_DEFAULT = "nstart,nconfig,nfriends,ncommands,nsorry"
BOT_COMPONENTS_TEST = "comp1,comp2"


class BotOwnerNameTests(MockedEnvironTestCase):
    def test_get_owner_name_default(self):
        with self.mocked_environ(f"{MODULE_PATH}.environ", None, ["BOT_OWNER_NAME"]):
            assert get_bot_owner_name() == BOT_OWNER_NAME_DEFAULT

    def test_get_owner_name_env(self):
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_OWNER_NAME": BOT_OWNER_NAME_TEST}
        ):
            assert get_bot_owner_name() == BOT_OWNER_NAME_TEST


class BotComponentsTests(MockedEnvironTestCase):
    def test_get_owner_name_default(self):
        with self.mocked_environ(f"{MODULE_PATH}.environ", None, ["BOT_COMPONENTS"]):
            assert get_bot_components() == BOT_COMPONENTS_DEFAULT

    def test_get_owner_name_env(self):
        with self.mocked_environ(
            f"{MODULE_PATH}.environ", {"BOT_COMPONENTS": BOT_COMPONENTS_TEST}
        ):
            assert get_bot_components() == BOT_COMPONENTS_TEST


class UserTests(TestCase):
    def test_init_friend(self):
        friend = User(0, "a")
        assert 0 == friend.id
        assert "a" == friend.username

    def test_init_friend_not_int(self):
        with self.assertRaises(ValueError):
            User("i", "a")


class CommandTests(TestCase):
    def test_init_command(self):
        command = Command("desc", "prod", "dev")
        assert "desc" == command.description
        assert "prod" == command.prod_command
        assert "dev" == command.dev_command


class ScheduleEntryTests(TestCase):
    def test_init_command(self):
        entry = ScheduleEntry("n", "s", "si")
        assert "n" == entry.name
        assert "s" == entry.schedule
        assert "si" == entry.signature
        assert entry.extra_args == {}

    def test_init_command_with_extra(self):
        entry = ScheduleEntry("n", "s", "si", extra_arg="extra_value")
        assert "n" == entry.name
        assert "s" == entry.schedule
        assert "si" == entry.signature
        assert {"extra_arg": "extra_value"} == entry.extra_args


class InlineHandlerTests(TestCase):
    def test_inline_handler_has_query(self):
        mocked_logger = MagicMock()
        mocker_update = MagicMock()
        mocker_update.callback_query.data = "data"

        def handler(_update=None, _context=None):
            return sentinel.handler_return

        result_function = inline_handler({"data": handler}, mocked_logger)
        result = result_function(mocker_update, None)
        mocked_logger.debug.assert_has_calls(
            [
                call("Received inline selection."),
                call("Inline selection was 'data'."),
            ]
        )
        assert sentinel.handler_return == result

    def test_inline_handler_hasnt_query(self):
        mocked_logger = MagicMock()
        mocker_update = MagicMock()
        mocker_update.callback_query.data = "other"

        result_function = inline_handler(
            {"data": lambda _update, _context: None},
            mocked_logger,
        )
        with self.assertRaises(ValueError) as e:
            result_function(mocker_update, None)
        mocked_logger.debug.assert_has_calls(
            [
                call("Received inline selection."),
                call("Inline selection was 'other'."),
            ]
        )
        assert "No valid handlers for query 'other'." == e.exception.args[0]


@patch(f"{MODULE_PATH}.LOG_VALUE_MAX_LENGHT", 6)
class QuoteValueForLogTests(TestCase):
    def test_quote_value_for_log_empty(self):
        result = quote_value_for_log("")
        assert "''" == result

    def test_quote_value_for_log_single(self):
        result = quote_value_for_log("a")
        assert "'a'" == result

    def test_quote_value_for_log_short(self):
        result = quote_value_for_log("aaa")
        assert "'aaa'" == result

    def test_quote_value_for_log_long(self):
        result = quote_value_for_log("aaabbbcccdddeeefffggghhhiii")
        assert "'aaabbb' (cropped to 6 chars)" == result
