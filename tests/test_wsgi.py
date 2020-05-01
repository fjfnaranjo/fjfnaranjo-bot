from unittest.mock import MagicMock, patch

from fjfnaranjobot.wsgi import application


@patch('fjfnaranjobot.wsgi.Bot')
def test_application_empty_path(_bot):
    def start_response_mock(status, _headers):
        assert '500' in status

    environ = MagicMock()
    application(environ, start_response_mock)