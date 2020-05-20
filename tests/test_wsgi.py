from io import BytesIO
from unittest.mock import MagicMock, patch

from fjfnaranjobot.wsgi import BotJSONError, BotLibraryError, BotTokenError, application
from fjfnaranjobot.wsgi import logger as wsgi_logger
from tests.base import BotTestCase

MODULE_PATH = 'fjfnaranjobot.wsgi'


class WSGITests(BotTestCase):
    def setUp(self):
        BotTestCase.setUp(self)

    def _fake_request(self, environ):
        def start_response_mock(status, headers):
            self._response_status = status
            self._response_headers = headers

        response_content = b''.join(application(environ, start_response_mock))
        return self._response_status, response_content, self._response_headers

    @patch(f'{MODULE_PATH}.Bot')
    def test_application_empty_path(self, _bot):
        environ = MagicMock()
        with self.assertLogs(wsgi_logger) as logs:
            status, content, _ = self._fake_request(environ)
            assert 0 == len(content)
            assert '500' in status
        assert 'empty path' in logs.output[0]

    @patch(f'{MODULE_PATH}.Bot')
    def test_application_regular_request(self, _bot):
        fakebot = MagicMock()
        fakebot.process_request.return_value = 'ok'
        _bot.return_value = fakebot
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '200' in status
        assert type(content) == bytes
        assert bytes('ok', 'utf8') == content
        assert 'Content-type' in headers_dict
        assert headers_dict['Content-type'] == 'text/plain'
        assert 'Content-Length' in headers_dict
        assert headers_dict['Content-Length'] == '2'

    @patch(f'{MODULE_PATH}.Bot')
    def test_application_bot_library_error(self, _bot):
        fakebot = MagicMock()
        fakebot.process_request.side_effect = BotLibraryError()
        _bot.return_value = fakebot
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
        assert 'Error from bot library' in logs.output[0]

    @patch(f'{MODULE_PATH}.Bot')
    def test_application_bot_json_error(self, _bot):
        fakebot = MagicMock()
        fakebot.process_request.side_effect = BotJSONError()
        _bot.return_value = fakebot
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
        assert 'Error from bot library (json)' in logs.output[0]

    @patch(f'{MODULE_PATH}.Bot')
    def test_application_bot_token_error(self, _bot):
        fakebot = MagicMock()
        fakebot.process_request.side_effect = BotTokenError()
        _bot.return_value = fakebot
        environ = {'PATH_INFO': '/', 'wsgi.input': BytesIO()}
        with self.assertLogs(wsgi_logger) as logs:
            status, content, headers = self._fake_request(environ)
        headers_dict = {key: value for key, value in headers}
        assert '404' in status
        assert type(content) == bytes
        assert 0 == len(content)
        assert 0 == len(headers_dict)
        assert 'Error from bot library (token)' in logs.output[0]
