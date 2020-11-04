from logging import DEBUG
from unittest import TestCase

from fjfnaranjobot.config import config, logger

MODULE_PATH = "fjfnaranjobot.config"


class ConfigTests(TestCase):
    def setUp(self):
        super().setUp()
        config.clear()

    def test_get_config_valid(self):
        for key in ["key", "key.key"]:
            with self.subTest(key=key):
                with self.assertRaises(KeyError):
                    with self.assertLogs(logger, DEBUG) as logs:
                        config[key]
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
                    config[key]
                assert f"No valid value for key {key}." == e.exception.args[0]

    def test_set_config_valid(self):
        for key in ["key", "key.key"]:
            with self.subTest(key=key):
                with self.assertLogs(logger, DEBUG) as logs:
                    config[key] = "val"
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
                    config[key] = "val"
                assert f"No valid value for key {key}." == e.exception.args[0]

    def test_set_config_get_config_persist(self):
        config["key"] = "val"
        assert "val" == config["key"]

    def test_get_config_dont_exists(self):
        with self.assertRaises(KeyError) as e:
            config["key"]
        assert f"The key 'key' don't exists." == e.exception.args[0]

    def test_set_config_replaces_old_value(self):
        config["key"] = "val"
        config["key"] = "newval"
        assert "newval" == config["key"]

    def test_config_len_empty(self):
        assert 0 == len(config)

    def test_config_len(self):
        config["key"] = "val"
        config["other.key"] = "other_val"
        assert 2 == len(config)

    def test_del_config_exists(self):
        config["key"] = "val"
        del config["key"]
        assert 0 == len(config)

    def test_del_config_dont_exists(self):
        with self.assertRaises(KeyError) as e:
            del config["key"]
        assert f"The key 'key' don't exists." == e.exception.args[0]
