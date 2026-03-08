from unittest import TestCase
from unittest.mock import MagicMock, call, patch, sentinel

from fjfnaranjobot.common import (
    ScheduleEntry,
    User,
    get_bot_components,
    get_bot_owner_name,
    quote_value_for_log,
)

from .base import MockedEnvironTestCase

MODULE_PATH = "fjfnaranjobot.common"

BOT_OWNER_NAME_DEFAULT = "fjfnaranjo"
BOT_OWNER_NAME_TEST = "owner"

BOT_COMPONENTS_DEFAULT = "start,config,friends,commands,sorry"
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
