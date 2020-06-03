from unittest import TestCase
from unittest.mock import patch

from celery import Celery

from fjfnaranjobot.tasks import app, setup_periodic_tasks, setup_tasks

MODULE_PATH = 'fjfnaranjobot.tasks'


class TasksTests(TestCase):
    def test_app_is_celery(self):
        assert isinstance(app, Celery)

    @patch(f'{MODULE_PATH}.app')
    @patch(f'{MODULE_PATH}.get_bot_components', return_value='component_mock9')
    @patch(f'{MODULE_PATH}._COMPONENTS_TEMPLATE', 'tests.component_mocks.{}')
    @patch(
        f'{MODULE_PATH}._TASKS_COMPONENTS_TEMPLATE', 'tests.component_mocks.{}.tasks'
    )
    def test_setup_tasks(self, _get_bot_components, app_mock):
        setup_tasks(app_mock)
        app_mock.autodiscover_tasks.assert_called_once_with(
            ['tests.component_mocks.component_mock9']
        )

    @patch(f'{MODULE_PATH}.app')
    @patch(f'{MODULE_PATH}.get_bot_components', return_value='')
    @patch(f'{MODULE_PATH}._COMPONENTS_TEMPLATE', 'tests.component_mocks.{}')
    @patch(
        f'{MODULE_PATH}._TASKS_COMPONENTS_TEMPLATE', 'tests.component_mocks.{}.tasks'
    )
    def test_setup_periodic_tasks(self, _get_bot_components, app_mock):
        # TODO: Implement this test
        setup_periodic_tasks(app_mock)
