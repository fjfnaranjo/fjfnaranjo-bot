from celery import Celery

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


app = Celery('tasks')


@app.task
def add(x, y):
    return x + y
