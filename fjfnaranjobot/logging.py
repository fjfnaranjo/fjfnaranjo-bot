from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from logging import getLogger as loggingGetLogger
from logging.config import dictConfig
from os import environ, makedirs, remove
from os.path import isdir, isfile, join, split

_BOT_LOGLEVEL_DEFAULT = 'INFO'

_configured = False

valid_log_levels = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}


def _configure_logging():
    log_level = environ.get('BOT_LOGLEVEL', _BOT_LOGLEVEL_DEFAULT)
    if log_level not in valid_log_levels:
        raise ValueError("Invalid level in BOT_LOGLEVEL var.")
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
                    'class': 'logging.StreamHandler',
                    'formatter': 'app',
                },
            },
            'loggers': {'app': {'level': log_level, 'handlers': ['app']}},
        }
    )


def reset_logging():
    global _configured
    if not _configured:
        return
    _configure_logging()


def getLogger(name, level=None):
    global _configured
    if not _configured:
        _configure_logging()
    logger = loggingGetLogger(f'app.{name}')
    if level is not None:
        logger.setLevel(level)
    return logger
