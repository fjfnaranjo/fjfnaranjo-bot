from collections import namedtuple
from logging import basicConfig, INFO

from fjfnaranjobot.bot import Bot, BotLibraryError, BotJSONError, BotTokenError


basicConfig(level=INFO)

bot = Bot()


Response = namedtuple('Response', ['status', 'headers', 'data'])


def application(environ, start_response):
    def prepare_text_response(text, status='200 OK', enconding='ascii'):
        data = bytes(text, enconding)
        status = status
        response_headers = [
            ('Content-type','text/plain'),
            ('Content-Length', str(len(data)))
        ]
        return Response(status, response_headers, [data])

    url_path = environ.get('RAW_URI', '/')
    response = Response('404 Not Found', [], [])

    request_body_size = 0
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        pass

    request_body = environ['wsgi.input'].read(request_body_size)

    try:
        response = prepare_text_response(
            bot.process_request(url_path, request_body)
        )
    except BotLibraryError as e:
        raise e
        response = prepare_text_response(
            str(e),
            status='500 Internal Server Error'
        )
    except BotJSONError as e:
        response = prepare_text_response(
            str(e),
            status='400 Bad Request'
        )
    except BotTokenError as e:
        # Default value for response is 404 Not Found
        pass

    start_response(response.status, response.headers)
    return iter(response.data)
