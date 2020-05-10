from importlib import import_module
from os import environ

from fjfnaranjobot.tasks import scheduler

BOT_COMPONENTS = environ.get('BOT_COMPONENTS', 'config,sorry,friends')


def main():
    for component in BOT_COMPONENTS.split(','):
        try:
            import_module(f'fjfnaranjobot.components.{component}.tasks')
        except ModuleNotFoundError:
            pass
    scheduler.run(True)


if __name__ == '__main__':
    main()
