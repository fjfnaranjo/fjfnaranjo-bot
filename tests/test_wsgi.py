from unittest.mock import patch, MagicMock

from fjfnaranjobot.wsgi import application


@patch('fjfnaranjobot.wsgi.Bot')
def test_application_empty_path(bot):
    def start_response_mock(status, headers):
        assert '500' in status
    environ = MagicMock()
    application(environ, start_response_mock)
