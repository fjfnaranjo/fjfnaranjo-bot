from importlib import import_module

from celery import Celery

from fjfnaranjobot.common import get_bot_components
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


_COMPONENTS_TEMPLATE = 'fjfnaranjobot.components.{}'
_TASKS_COMPONENTS_TEMPLATE = 'fjfnaranjobot.components.{}.tasks'


app = Celery('tasks')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    for component in get_bot_components().split(','):
        try:
            component_tasks = import_module(
                _TASKS_COMPONENTS_TEMPLATE.format(component)
            )

        except ModuleNotFoundError:
            pass
        else:
            try:
                schedule = component_tasks.schedule
            except AttributeError:
                pass
            else:
                for entry in schedule:
                    schedule_def = schedule[entry].copy()
                    del schedule_def['schedule']
                    del schedule_def['signature']
                    sender.add_periodic_task(
                        schedule[entry]['schedule'],
                        schedule[entry]['signature'],
                        name=entry,
                        **schedule_def
                    )


@app.on_after_finalize.connect
def setup_tasks(sender, **_kwargs):
    sender.autodiscover_tasks(
        [
            _COMPONENTS_TEMPLATE.format(component)
            for component in get_bot_components().split(',')
        ],
    )
