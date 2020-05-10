from importlib import import_module
from os import environ
from sched import scheduler as Scheduler
from time import sleep, time

from fjfnaranjobot.logging import getLogger

BOT_COMPONENTS = environ.get('BOT_COMPONENTS', 'config,sorry,friends')

logger = getLogger(__name__)
scheduler = Scheduler(time, sleep)


class PeriodicEvent:
    '''
    Decorates a function and call it each n seconds. args and kwargs will be
    used to call the function. When the function is called directly, the new
    args and kwargs received will be mixed with the decorator args and kwargs
    behaving as it was a partial.
    '''

    def __init__(self, seconds, *args, **kwargs):
        if callable(seconds):
            raise ValueError('PeriodicEvent decorator requires the number of seconds.')
        self.seconds = seconds
        self.periodic_args = args
        self.periodic_kwargs = kwargs

    def __call__(self, function):
        self.function = function
        self.schedule_next()

        def direct_call(*args, **kwargs):
            function_args = self.periodic_args + args
            function_kwargs = self.periodic_kwargs.copy()
            function_kwargs.update(kwargs)
            self.function(*function_args, **function_kwargs)

        return direct_call

    def schedule_next(self):
        logger.debug(f"Scheduling {self.function} to run every {self.seconds} seconds.")
        scheduler.enter(self.seconds, 0, self.exec_function)

    def exec_function(self):
        logger.debug(f"Executing scheduled {self.function}.")
        self.function(*self.periodic_args, **self.periodic_kwargs)
        self.schedule_next()


def main():
    for component in BOT_COMPONENTS.split(','):
        try:
            import_module(f'fjfnaranjobot.components.{component}.events')
        except ModuleNotFoundError:
            pass
    scheduler.run(True)


if __name__ == '__main__':
    main()
