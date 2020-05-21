from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from logging import getLogger as loggingGetLogger
from logging.config import dictConfig
from os import environ, makedirs, remove
from os.path import isdir, isfile, join, split

from fjfnaranjobot.bot import EnvValueError, get_bot_data_dir

_BOT_LOGFILE_DEFAULT = 'bot.log'
_BOT_LOGLEVEL_DEFAULT = 'INFO'

valid_log_levels = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}


_state = {'initialized': False}


def _get_log_path():
    return join(get_bot_data_dir(), environ.get('BOT_LOGFILE', _BOT_LOGFILE_DEFAULT))


def _configure_logging():
    log_path = _get_log_path()
    log_level = environ.get('BOT_LOGLEVEL', _BOT_LOGLEVEL_DEFAULT)
    log_dir, _ = split(log_path)
    if not isdir(log_dir):
        try:
            makedirs(log_dir)
        except:
            raise EnvValueError('Invalid dir name in BOT_LOGFILE var.')
    new_file = False
    if not isfile(log_path):
        try:
            with open(log_path, 'wb'):
                pass
            new_file = True
        except OSError:
            raise EnvValueError('Invalid file name in BOT_LOGFILE var.')
    if log_level not in valid_log_levels:
        raise EnvValueError('Invalid level in BOT_LOGLEVEL var.')
    dictConfig(
        {
            'version': 1,
            'formatters': {
                'app': {
                    'format': '{asctime} {levelname} [{name}] {msg}',
                    'style': '{',
                },
            },
            'handlers': {
                'app': {
                    'class': 'logging.FileHandler',
                    'formatter': 'app',
                    'filename': log_path,
                },
            },
            'loggers': {'app': {'level': log_level, 'handlers': ['app']}},
        }
    )
    if new_file:
        loggingGetLogger('app').info('Log created.')
    _state['initialized'] = True


def reset():
    _state['initialized'] = False
    log_path = _get_log_path()
    if isfile(log_path):
        remove(log_path)
    _configure_logging()


def getLogger(name, level=None):
    if not _state['initialized']:
        _configure_logging()
    logger = loggingGetLogger(f'app.{name}')
    if level is not None:
        logger.setLevel(level)
    return logger
