from os import remove
from os.path import join, isfile

from fjfnaranjobot.config import BOT_DATA_DIR, BOT_DB, state, get_key, set_key
from tests.base import BotTestCase


class ConfigTests(BotTestCase):
    def setUp(self):
        state['initialized'] = False
        db_file = join(BOT_DATA_DIR, BOT_DB)
        if isfile(db_file):
            remove(db_file)

    def test_init_config_get(self):
        get_key('key')
        assert isfile(join(BOT_DATA_DIR, BOT_DB))

    def test_init_config_set(self):
        set_key('key', 'val')
        assert isfile(join(BOT_DATA_DIR, BOT_DB))

    def test_store_retrieve_value(self):
        set_key('key', 'val')
        val = get_key('key')
        assert 'val' == val

    def test_retrieve_value_dont_exists(self):
        val = get_key('key')
        assert None == val
