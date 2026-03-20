from unittest import TestCase
from unittest.mock import call, patch

from celery import Celery

from fjfnaranjobot.tasks import app, setup_periodic_tasks, setup_tasks

MODULE_PATH = "fjfnaranjobot.tasks"


class TasksTests(TestCase):
    def test_app_is_celery(self):
        assert isinstance(app, Celery)


@patch(f"{MODULE_PATH}.app")
@patch(f"{MODULE_PATH}.get_bot_components", return_value="comp1,comp2")
@patch(f"{MODULE_PATH}._COMPONENTS_TEMPLATE", "c.{}")
class TasksSetupTests(TestCase):
    def test_setup_tasks(self, _get_bot_components, app_mock):
        setup_tasks(app_mock)
        app_mock.autodiscover_tasks.assert_called_once_with(["c.comp1", "c.comp2"])


@patch(f"{MODULE_PATH}.app")
@patch(
    f"{MODULE_PATH}._TASKS_COMPONENTS_TEMPLATE", "tests.component_mocks.tasks.{}.tasks"
)
class TasksSetupPeriodicTests(TestCase):
    @patch(f"{MODULE_PATH}.get_bot_components", return_value="")
    def test_no_components(self, _get_bot_components, app):
        setup_periodic_tasks(app)
        app.add_periodic_task.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock1")
    def test_component_without_info(self, _get_bot_components, app):
        setup_periodic_tasks(app)
        app.add_periodic_task.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock2")
    def test_component_with_no_entries(self, _get_bot_components, app):
        setup_periodic_tasks(app)
        app.add_periodic_task.assert_not_called()

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock3")
    def test_component_with_invalid_entries(self, _get_bot_components, app):
        with self.assertRaises(ValueError) as e:
            setup_periodic_tasks(app)
        assert (
            "Invalid schedule definitions for component 'component_mock3'."
            == e.exception.args[0]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock4")
    def test_component_with_invalid_entry(self, _get_bot_components, app):
        with self.assertRaises(ValueError) as e:
            setup_periodic_tasks(app)
        assert (
            "Invalid schedule entry for component 'component_mock4'."
            == e.exception.args[0]
        )

    @patch(f"{MODULE_PATH}.get_bot_components", return_value="component_mock5")
    def test_component_with_ok_entries(self, _get_bot_components, app):
        setup_periodic_tasks(app)
        assert 2 == app.add_periodic_task.call_count
        assert call("s", "si", name="n") == app.add_periodic_task.mock_calls[0]
        assert (
            call("s", "si", name="n", extra_arg="e")
            == app.add_periodic_task.mock_calls[1]
        )
