from importlib import import_module
from inspect import getmembers, isclass
from json import JSONDecodeError, loads
from os import environ

from telegram import Update
from telegram.ext import Application

from fjfnaranjobot.command import BotCommandError, Command
from fjfnaranjobot.common import command_list, get_bot_components
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

BOT_TOKEN = environ.get("BOT_TOKEN")
BOT_WEBHOOK_URL = environ.get("BOT_WEBHOOK_URL", "")
BOT_WEBHOOK_TOKEN = environ.get("BOT_WEBHOOK_TOKEN", "")
BOT_WEBHOOK_CERT = environ.get("BOT_WEBHOOK_CERT", "")


_BOT_COMPONENTS_TEMPLATE = "fjfnaranjobot.components.{}.info"

_state = {"bot": None}


class BotJSONError(Exception):
    pass


class BotTokenError(Exception):
    pass


# TODO: Check and test BOT_TOKEN not defined
class Bot:
    def __init__(self):
        builder = Application.builder()
        builder.token(BOT_TOKEN)
        builder.updater(None)
        self.application = builder.build()
        self.bot = self.application.bot
        self.webhook_url = "/".join((BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN))
        logger.debug("Bot init done.")
        self.application.add_error_handler(self._log_error_from_context)
        for component in get_bot_components().split(","):
            logger.debug(f"Parsing component {component}.")
            self._parse_component_info(component)
        logger.debug("Bot handlers registered.")

    def _log_error_from_context(self, _update, context):
        logger.exception(
            "Error inside the framework raised by the application.",
            exc_info=context.error,
        )

    def _register_command(self, command):
        for group, handler, class_name in command.handlers:
            command.log_handler(group, handler)
            # TODO: Remove this log and 3rd component in handlers (not used anymore)
            logger.debug(f"Adding handler {class_name}.")
            self.application.add_handler(handler, group)

    def _parse_component_info(self, component):
        component_module = _BOT_COMPONENTS_TEMPLATE.format(component)
        try:
            info = import_module(component_module)
        except ModuleNotFoundError:
            pass
        else:

            def predicate(value):
                return (
                    isclass(value)
                    and issubclass(value, Command)
                    and hasattr(value, "__module__")
                    and value.__module__.startswith(component_module)
                )

            members = getmembers(info, predicate=predicate)
            for _, member in members:
                command = member()
                command_list.append(command)
                try:
                    self._register_command(command)
                except BotCommandError:
                    raise RuntimeError(
                        "BotCommandError raised trying to register "
                        f"'{component}' component handlers."
                    )

    async def process_request(self, url_path, update):
        # Root URL
        if url_path == "" or url_path == "/":
            logger.info("Reply with salute.")
            return "I'm fjfnaranjo's bot."

        # Healt check URL
        elif url_path == "/ping":
            logger.info("Reply with pong.")
            return "pong"

        # Register webhook request URL
        elif url_path == ("/" + "/".join((BOT_WEBHOOK_TOKEN, "register_webhook"))):
            await self.bot.set_webhook(url=self.webhook_url, drop_pending_updates=True)
            logger.info("Reply with ok to register_webhook.")
            return "ok"

        # Register webhook request URL (using self signed cert)
        elif url_path == ("/" + "/".join((BOT_WEBHOOK_TOKEN, "register_webhook_self"))):
            await self.bot.set_webhook(
                url=self.webhook_url,
                certificate=open(BOT_WEBHOOK_CERT, "rb"),
                drop_pending_updates=True,
            )
            logger.info("Reply with ok to register_webhook_self.")
            return "ok (self)"

        # Don't allow other URLs unless preceded by token
        elif url_path != "/" + BOT_WEBHOOK_TOKEN:
            shown_url = url_path[:10]
            logger.info(
                f"Path '{shown_url}' (cropped to 10 chars) not preceded by token and not handled by bot."
            )
            raise BotTokenError(
                f"Path '{shown_url}' (cropped to 10 chars) not preceded by token and not handled by bot."
            )

        # Parse response to bot library
        try:
            update_json = loads(update)
        except JSONDecodeError as e:
            logger.info("Received non-JSON request.")
            raise BotJSONError("Sent content isn't JSON.") from e

        # Delegate response to bot library
        logger.debug("Dispatch update to library.")
        await self.application.update_queue.put(Update.de_json(update_json, self.bot))
        return "ok"


# TODO: Test
def ensure_bot():
    if _state["bot"] is not None:
        return _state["bot"]
    _state["bot"] = Bot()
    return _state["bot"]
