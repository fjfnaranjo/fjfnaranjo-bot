from multiprocessing import Process
from sched import scheduler as Scheduler
from time import sleep, time

from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)
scheduler = Scheduler(time, sleep)


class _PeriodicEvent:
    def __init__(self, seconds, action, *args, **kwargs):
        self.seconds = seconds
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.schedule_next()

    def schedule_next(self):
        logger.debug(f"Scheduling {self.action} to run every {self.seconds} seconds.")
        scheduler.enter(self.seconds, 0, self.exec_action)

    def exec_action(self):
        logger.debug(f"Executing scheduled {self.action}.")
        self.action(*self.args, **self.kwargs)
        self.schedule_next()


def each(seconds):
    def decorator(f):
        _PeriodicEvent(seconds, f)

    return decorator


def start_scheduling():
    runner = Process(target=scheduler.run)
    runner.start()
