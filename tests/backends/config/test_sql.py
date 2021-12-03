from logging import DEBUG
from unittest import TestCase

from fjfnaranjobot.backends import sqldb
from fjfnaranjobot.backends.config.sql import SQLConfiguration, logger


class SQLConfigTests(TestCase):
    def setUp(self):
        super().setUp()
        self.sql_config = SQLConfiguration(sqldb)

    def tearDown(self):
        all_keys = list(self.sql_config.keys())
        for key in all_keys:
            del self.sql_config[key]
        super().tearDown()

    def test_get_config_valid(self):
        for key in ["key", "key.key"]:
            with self.subTest(key=key):
                with self.assertRaises(KeyError):
                    with self.assertLogs(logger, DEBUG) as logs:
                        self.sql_config[key]
                assert f"Getting configuration value for key '{key}'." in logs.output[0]

    def test_get_config_invalid(self):
        for key in [
            ".key",
            "key.",
            "key key",
            "!a_invalid_key",
            "this.key.is.ok.but.very.long",
        ]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError) as e:
                    self.sql_config[key]
                assert f"No valid value for key {key}." == e.exception.args[0]

    def test_set_config_valid(self):
        for key in ["key", "key.key"]:
            with self.subTest(key=key):
                with self.assertLogs(logger, DEBUG) as logs:
                    self.sql_config[key] = "val"
                assert (
                    f"Setting configuration key '{key}' to value 'val' (cropped to 10 chars)."
                    in logs.output[0]
                )

    def test_set_config_invalid(self):
        for key in [
            ".key",
            "key.",
            "key key",
            "!a_invalid_key",
            "this.key.is.ok.but.very.long",
        ]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError) as e:
                    self.sql_config[key] = "val"
                assert f"No valid value for key {key}." == e.exception.args[0]

    def test_set_config_get_config_persist(self):
        self.sql_config["key"] = "val"
        assert "val" == self.sql_config["key"]

    def test_get_config_dont_exists(self):
        with self.assertRaises(KeyError) as e:
            self.sql_config["key"]
        assert f"The key 'key' don't exists." == e.exception.args[0]

    def test_set_config_replaces_old_value(self):
        self.sql_config["key"] = "val"
        self.sql_config["key"] = "newval"
        assert "newval" == self.sql_config["key"]

    def test_config_len_empty(self):
        assert 0 == len(self.sql_config)

    def test_config_len(self):
        self.sql_config["key"] = "val"
        self.sql_config["other.key"] = "other_val"
        assert 2 == len(self.sql_config)

    def test_del_config_exists(self):
        self.sql_config["key"] = "val"
        del self.sql_config["key"]
        assert 0 == len(self.sql_config)

    def test_del_config_dont_exists(self):
        with self.assertRaises(KeyError) as e:
            del self.sql_config["key"]
        assert f"The key 'key' don't exists." == e.exception.args[0]
