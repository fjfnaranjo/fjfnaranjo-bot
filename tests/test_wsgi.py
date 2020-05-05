from unittest import TestCase
from unittest.mock import MagicMock, patch

from fjfnaranjobot.wsgi import application


MODULE_PATH = 'fjfnaranjobot.wsgi'


class WSGITests(TestCase):
    @patch(f'{MODULE_PATH}.Bot')
    def test_application_empty_path(self, _bot):
        def start_response_mock(status, _headers):
            assert '500' in status

        environ = MagicMock()
        application(environ, start_response_mock)
