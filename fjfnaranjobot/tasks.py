from celery import Celery

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


app = Celery('tasks')
