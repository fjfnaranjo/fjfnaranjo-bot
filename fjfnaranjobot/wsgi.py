from collections import namedtuple

from fjfnaranjobot.bot import Bot, BotJSONError, BotLibraryError, BotTokenError
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


Response = namedtuple('Response', ['status', 'headers', 'data'])


def application(environ, start_response):
    def prepare_text_response(text, status='200 OK', enconding='ascii'):
        data = bytes(text, enconding)
        status = status
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(data))),
        ]
        return Response(status, response_headers, [data])

    bot = Bot()

    url_path = environ.get('PATH_INFO', '')

    if len(url_path) == 0:
        logger.error('Received empty path in WSGI request.')
        response = prepare_text_response(str(''), status='500 Internal Server Error')

    else:
        content_length = environ.get('CONTENT_LENGTH', '')
        request_body_size = int(content_length) if len(content_length) > 0 else 0
        request_body = environ['wsgi.input'].read(request_body_size)

        try:
            logger.debug('Defer request to bot for processing')
            response = prepare_text_response(
                bot.process_request(url_path, request_body)
            )
        except BotLibraryError as e:
            logger.exception('Error from bot library', exc_info=e)
            response = prepare_text_response(str(e), status='500 Internal Server Error')
        except BotJSONError as e:
            logger.exception('Error from bot library (json)', exc_info=e)
            response = prepare_text_response(str(e), status='400 Bad Request')
        except BotTokenError as e:
            logger.exception('Error from bot library (token)', exc_info=e)
            response = Response('404 Not Found', [], [])

    start_response(response.status, response.headers)
    return iter(response.data)
