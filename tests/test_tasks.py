from unittest import TestCase

from celery import Celery

from fjfnaranjobot.tasks import app


class TasksTests(TestCase):
    def test_app_is_celery(self):
        assert isinstance(app, Celery)
