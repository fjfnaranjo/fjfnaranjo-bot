from io import BytesIO
from logging import DEBUG
from unittest.mock import MagicMock, patch

from fjfnaranjobot.bot import BotFrameworkError, BotJSONError, BotTokenError
from fjfnaranjobot.wsgi import application
from fjfnaranjobot.wsgi import logger as wsgi_logger

from .base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.wsgi'


@patch(f'{MODULE_PATH}.bot')
class WSGITests(BotTestCase):
    def _fake_request(self, environ):
        def start_response_mock(status, headers):
            self._response_status = status
            self._response_headers = headers

        response_content = b''.join(application(environ, start_response_mock))
        return self._response_status, response_content, self._response_headers

    def test_application_empty_path(self, _bot):
        environ = MagicMock()
        with self.assertLogs(wsgi_logger) as logs:
            status, content, _ = self._fake_request(environ)
            assert 0 == len(content)
            assert '500' in status
        assert 'Received empty path in WSGI request.' in logs.output[0]

    def test_application_regular_request(self, bot):
        bot.process_request.return_value = 'ok'
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        with self.assertLogs(wsgi_logger, DEBUG) as logs:
            status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '200' in status
        assert type(content) == bytes
        assert bytes('ok', 'utf8') == content
        assert 'Content-type' in headers_dict
        assert headers_dict['Content-type'] == 'text/plain'
        assert 'Content-Length' in headers_dict
        assert headers_dict['Content-Length'] == '2'
        assert 'Defer request to bot for processing.' in logs.output[0]

    def test_application_bot_library_error(self, bot):
        bot.process_request.side_effect = BotFrameworkError()
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        with self.assertLogs(wsgi_logger) as logs:
            status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '500' in status
        assert type(content) == bytes
        assert 0 == len(content)
        assert 'Content-type' in headers_dict
        assert headers_dict['Content-type'] == 'text/plain'
        assert 'Content-Length' in headers_dict
        assert headers_dict['Content-Length'] == '0'
        assert 'Error from bot framework.' in logs.output[0]

    def test_application_bot_json_error(self, bot):
        bot.process_request.side_effect = BotJSONError()
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        with self.assertLogs(wsgi_logger) as logs:
            status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '400' in status
        assert type(content) == bytes
        assert 0 == len(content)
        assert 'Content-type' in headers_dict
        assert headers_dict['Content-type'] == 'text/plain'
        assert 'Content-Length' in headers_dict
        assert headers_dict['Content-Length'] == '0'
        assert 'Error from bot framework (json).' in logs.output[0]

    def test_application_bot_token_error(self, bot):
        bot.process_request.side_effect = BotTokenError()
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        with self.assertLogs(wsgi_logger) as logs:
            status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '404' in status
        assert type(content) == bytes
        assert 0 == len(content)
        assert 0 == len(headers_dict)
        assert 'Error from bot framework (token).' in logs.output[0]
