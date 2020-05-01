from os import environ, access, W_OK

from logging import getLogger as loggingGetLogger, INFO, DEBUG, WARNING, ERROR, CRITICAL
from logging.config import dictConfig


BOT_LOGFILE = environ.get('BOT_LOGFILE')
BOT_LOGLEVEL = environ.get('BOT_LOGLEVEL', 'INFO')

valid_log_levels = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}


_configured = False


def configure_logging():
    if not access(BOT_LOGFILE, W_OK):
        raise ValueError('Invalid file name in BOT_LOGFILE var.')
    if BOT_LOGLEVEL not in valid_log_levels:
        raise ValueError('Invalid level in BOT_LOGLEVEL var.')
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
                    'filename': BOT_LOGFILE,
                },
            },
            'loggers': {'app': {'level': BOT_LOGLEVEL, 'handlers': ['app']}},
        }
    )


def getLogger(name, level=None):
    global _configured
    if not _configured:
        configure_logging()
        _configured = True
    logger = loggingGetLogger(f'app.{name}')
    if level is not None:
        logger.setLevel(level)
    return logger
