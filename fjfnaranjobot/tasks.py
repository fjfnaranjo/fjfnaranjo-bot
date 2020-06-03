from celery import Celery

from fjfnaranjobot.common import get_bot_components
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


_TASKS_COMPONENTS_TEMPLATE = 'fjfnaranjobot.components.{}'


app = Celery('tasks')
app.autodiscover_tasks(
    [
        _TASKS_COMPONENTS_TEMPLATE.format(component)
        for component in get_bot_components().split(',')
    ],
)
