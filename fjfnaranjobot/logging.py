from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from logging import getLogger as loggingGetLogger
from logging.config import dictConfig
from os import W_OK, access, environ

from fjfnaranjobot.utils import EnvValueError

_BOT_LOGFILE = environ.get('BOT_LOGFILE')
_BOT_LOGLEVEL = environ.get('BOT_LOGLEVEL', 'INFO')

valid_log_levels = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}


state = {'configured': False}


def _configure_logging():
    if not access(_BOT_LOGFILE, W_OK):
        raise EnvValueError('Invalid file name in BOT_LOGFILE var.')
    if _BOT_LOGLEVEL not in valid_log_levels:
        raise EnvValueError('Invalid level in BOT_LOGLEVEL var.')
    dictConfig(
        {
            'version': 1,
            'formatters': {
                'app': {'format': '{asctime} {levelname} [{name}] {msg}', 'style': '{'},
            },
            'handlers': {
                'app': {
                    'class': 'logging.FileHandler',
                    'formatter': 'app',
                    'filename': _BOT_LOGFILE,
                },
            },
            'loggers': {'app': {'level': _BOT_LOGLEVEL, 'handlers': ['app']}},
        }
    )


def getLogger(name, level=None):
    if not state['configured']:
        _configure_logging()
        state['configured'] = True
    logger = loggingGetLogger(f'app.{name}')
    if level is not None:
        logger.setLevel(level)
    return logger
