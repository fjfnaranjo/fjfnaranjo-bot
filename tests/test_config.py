from logging import DEBUG

from fjfnaranjobot.config import InvalidKeyError, get_config, logger, reset, set_config

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.config'


class ConfigTests(BotTestCase):
    def test_get_config_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                with self.assertRaises(KeyError):
                    with self.assertLogs(logger, DEBUG) as logs:
                        get_config(key)
                assert (
                    f'Getting configuration value for key \'{key}\'.' in logs.output[0]
                )

    def test_get_config_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError) as e:
                    get_config(key)
                assert f'No valid value for key {key}.' in str(e.exception)

    def test_set_config_valid(self):
        for key in ['key', 'key.key']:
            with self.subTest(key=key):
                with self.assertLogs(logger, DEBUG) as logs:
                    set_config(key, 'val')
                assert (
                    f'Setting configuration key \'{key}\' to value \'val\' (cropped to 10 chars).'
                    in logs.output[0]
                )

    def test_set_config_invalid(self):
        for key in [
            '.key',
            'key.',
            'key key',
            '!a_invalid_key',
        ]:
            with self.subTest(key=key):
                with self.assertRaises(InvalidKeyError) as e:
                    set_config(key, 'val')
                assert f'No valid value for key {key}.' in str(e.exception)

    def test_set_config_get_config_persist(self):
        reset()
        set_config('key', 'val')
        val = get_config('key')
        assert 'val' == val

    def test_get_config_dont_exists(self):
        reset()
        with self.assertRaises(KeyError) as e:
            get_config('key')
        assert f'The key \'key\' don\'t exists.' in str(e.exception)

    def test_set_config_replaces_old_value(self):
        reset()
        set_config('key', 'val')
        set_config('key', 'val2')
        val = get_config('key')
        assert 'val2' == val
