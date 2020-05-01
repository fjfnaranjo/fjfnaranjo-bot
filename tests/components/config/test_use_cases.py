from unittest.mock import patch, MagicMock


from fjfnaranjobot.components.config.use_cases import config_set, config_get


@patch('fjfnaranjobot.components.config.use_cases.set_key')
@patch('telegram.update.Update')
@patch('telegram.bot.Bot')
def test_config_set(_bot, _update, set_key):
    update = MagicMock()
    update.message.text = f'cmd key val'
    config_set(None, update)
    set_key.assert_called_once_with('key', 'val')


@patch('fjfnaranjobot.components.config.use_cases.get_key')
@patch('telegram.update.Update')
@patch('telegram.bot.Bot')
def test_config_get(_bot, _update, get_key):
    update = MagicMock()
    update.message.text = f'cmd key'
    config_get(None, update)
    get_key.assert_called_once_with('key')
