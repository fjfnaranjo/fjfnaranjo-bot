from importlib import import_module
from warnings import filterwarnings

from celery import Celery

from fjfnaranjobot.common import ScheduleEntry, get_bot_components
from fjfnaranjobot.logging import getLogger

filterwarnings("ignore", ".*per_message=False.*CallbackQueryHandler.*", UserWarning)

logger = getLogger(__name__)

_COMPONENTS_TEMPLATE = "fjfnaranjobot.components.{}"
_TASKS_COMPONENTS_TEMPLATE = "fjfnaranjobot.components.{}.tasks"


app = Celery("tasks")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    for component in get_bot_components().split(","):
        try:
            component_tasks = import_module(
                _TASKS_COMPONENTS_TEMPLATE.format(component)
            )
        except ModuleNotFoundError:
            pass
        else:
            try:
                schedule = list(component_tasks.schedule)
            except AttributeError:
                pass
            except TypeError:
                raise ValueError(
                    f"Invalid schedule definitions for component '{component}'."
                )
            else:
                for entry in schedule:
                    if not isinstance(entry, ScheduleEntry):
                        raise ValueError(
                            f"Invalid schedule entry for component '{component}'."
                        )
                    sender.add_periodic_task(
                        entry.schedule,
                        entry.signature,
                        name=entry.name,
                        **entry.extra_args,
                    )


@app.on_after_finalize.connect
def setup_tasks(sender, **_kwargs):
    sender.autodiscover_tasks(
        [
            _COMPONENTS_TEMPLATE.format(component)
            for component in get_bot_components().split(",")
        ],
    )
