# TODO: Clean _n and _N
from importlib import import_module
from inspect import getmembers, isclass
from json import JSONDecodeError, loads
from os import environ

from telegram import Bot as TBot
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Dispatcher,
    Handler,
    MessageHandler,
    StringCommandHandler,
)
from telegram.ext.dispatcher import DEFAULT_GROUP

from fjfnaranjobot.command import BotCommand
from fjfnaranjobot.common import Command, command_list, get_bot_components
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

BOT_TOKEN = environ.get("BOT_TOKEN")
BOT_WEBHOOK_URL = environ.get("BOT_WEBHOOK_URL", "")
BOT_WEBHOOK_TOKEN = environ.get("BOT_WEBHOOK_TOKEN", "")
BOT_WEBHOOK_CERT = environ.get("BOT_WEBHOOK_CERT", "")


_BOT_COMPONENTS_TEMPLATE = "fjfnaranjobot.components.{}.info"
_N_BOT_COMPONENTS_TEMPLATE = "fjfnaranjobot.components.{}.ninfo"

_state = {"bot": None}


class BotJSONError(Exception):
    pass


class BotTokenError(Exception):
    pass


def _get_handler_callback_name(handler):
    callback_function = getattr(handler, "callback", None)
    return (
        callback_function.__name__
        if callback_function is not None and callable(callback_function)
        else "<unknown callback>"
    )


# TODO: Check and test BOT_TOKEN not defined
class Bot:
    def __init__(self):
        self.bot = TBot(BOT_TOKEN)
        self.dispatcher = Dispatcher(self.bot, None, workers=0, use_context=True)
        self.dispatcher.add_error_handler(self._log_error_from_context)
        self.webhook_url = "/".join((BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN))
        logger.debug("Bot init done.")
        for component in get_bot_components().split(","):
            self._parse_component_info(component)
            self._n_parse_component_info(component)
        logger.debug("Bot handlers registered.")

    def _log_error_from_context(self, _update, context):
        logger.exception(
            "Error inside the framework raised by the dispatcher.",
            exc_info=context.error,
        )

    def _get_names_callbacks(self, handler):
        names_callbacks = []

        if isinstance(handler, ConversationHandler):
            for entry_point in handler.entry_points:
                return self._get_names_callbacks(entry_point)
        else:
            callback_name = _get_handler_callback_name(handler)
            if isinstance(handler, CommandHandler):
                for command in handler.command:
                    names_callbacks.append(
                        (
                            command,
                            callback_name,
                        )
                    )
            elif isinstance(handler, StringCommandHandler):
                names_callbacks.append(
                    (
                        handler.command,
                        callback_name,
                    )
                )
            elif isinstance(handler, MessageHandler):
                names_callbacks.append(
                    (
                        "<message>",
                        callback_name,
                    )
                )
            else:
                names_callbacks.append(
                    (
                        "<unknown command>",
                        callback_name,
                    )
                )

        return names_callbacks

    def _parse_component_handlers(self, component, info, group):
        try:
            handlers = list(info.handlers)
        except AttributeError:
            pass
        except TypeError:
            raise ValueError(
                f"Invalid handlers definition for component '{component}'."
            )
        else:
            for handler in handlers:
                if not isinstance(handler, Handler):
                    raise ValueError(f"Invalid handler for component '{component}'.")
                else:
                    self.dispatcher.add_handler(handler, group)
                    callback_names = self._get_names_callbacks(handler)
                    for command, callback in callback_names:
                        logger.debug(
                            f"Registered command '{command}' "
                            f"with callback '{callback}' "
                            f"for component '{component}' "
                            f"and group number {group}."
                        )

    def _parse_component_commands(self, component, info):
        try:
            commands = info.commands
        except AttributeError:
            pass
        else:
            for command in commands:
                if not isinstance(command, Command):
                    raise ValueError(f"Invalid command for component '{component}'.")
                command_list.append(command)

    def _parse_component_info(self, component):
        try:
            info = import_module(_BOT_COMPONENTS_TEMPLATE.format(component))
        except ModuleNotFoundError:
            pass
        else:
            try:
                group = int(getattr(info, "group", DEFAULT_GROUP))
            except ValueError:
                raise ValueError(f"Invalid group for component '{component}'.")
            self._parse_component_handlers(component, info, group)
            self._parse_component_commands(component, info)

    def _n_parse_component_info(self, component):
        try:
            info = import_module(_N_BOT_COMPONENTS_TEMPLATE.format(component))
        except ModuleNotFoundError:
            pass
        else:
            members = getmembers(info)
            for _, member in members:
                if (
                    member is not BotCommand
                    and isclass(member)
                    and issubclass(member, BotCommand)
                ):
                    command = member()
                    command_list.append(command)
                    for group, handler in command.handlers:
                        self.dispatcher.add_handler(handler, group)

    def process_request(self, url_path, update):

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
            self.bot.set_webhook(url=self.webhook_url)
            logger.info("Reply with ok to register_webhook.")
            return "ok"

        # Register webhook request URL (using self signed cert)
        elif url_path == ("/" + "/".join((BOT_WEBHOOK_TOKEN, "register_webhook_self"))):
            self.bot.set_webhook(
                url=self.webhook_url,
                certificate=open(BOT_WEBHOOK_CERT, "rb"),
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
        self.dispatcher.process_update(Update.de_json(update_json, self.bot))

        return "ok"


# TODO: Test
def ensure_bot():
    if _state["bot"] is not None:
        return _state["bot"]
    _state["bot"] = Bot()
    return _state["bot"]
