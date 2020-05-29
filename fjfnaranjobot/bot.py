from importlib import import_module
from json import JSONDecodeError, loads
from os import environ

from telegram import Bot as TBot
from telegram import Update
from telegram.ext import Dispatcher, Handler
from telegram.ext.dispatcher import DEFAULT_GROUP

from fjfnaranjobot.common import get_names_callbacks
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

BOT_TOKEN = environ.get('BOT_TOKEN')
BOT_WEBHOOK_URL = environ.get('BOT_WEBHOOK_URL')
BOT_WEBHOOK_TOKEN = environ.get('BOT_WEBHOOK_TOKEN')
BOT_COMPONENTS = environ.get('BOT_COMPONENTS', 'config,friends,sorry')

_BOT_COMPONENTS_TEMPLATE = 'fjfnaranjobot.components.{}.handlers'


class BotFrameworkError(Exception):
    pass


class BotJSONError(Exception):
    pass


class BotTokenError(Exception):
    pass


class Bot:
    def __init__(self):
        self.bot = TBot(BOT_TOKEN)
        self.dispatcher = Dispatcher(self.bot, None, workers=0, use_context=True)
        self.webhook_url = '/'.join((BOT_WEBHOOK_URL, BOT_WEBHOOK_TOKEN))
        logger.debug("Bot init done.")
        self._command_list = []
        self._init_handlers()
        logger.debug("Bot handlers registered.")

    def _init_handlers(self):
        for component in BOT_COMPONENTS.split(','):
            try:
                info = import_module(_BOT_COMPONENTS_TEMPLATE.format(component))
                try:
                    handlers = info.handlers
                except AttributeError:
                    pass
                else:
                    try:
                        group = int(getattr(info, 'group', DEFAULT_GROUP))
                    except ValueError:
                        raise ValueError(f"Invalid group for component '{component}'.")
                    for handler in handlers:
                        if not isinstance(handler, Handler):
                            raise ValueError(
                                f"Invalid handler for component '{component}'."
                            )
                        else:
                            self.dispatcher.add_handler(handler, group)
                            callback_names = get_names_callbacks(handler)
                            for command, callback in callback_names:
                                if not command.startswith('<'):
                                    self._command_list.append(command)
                                logger.debug(
                                    f"Registered command '{command}' "
                                    f"with callback '{callback}' "
                                    f"for component '{component}' "
                                    f"and group number {group}."
                                )

            except ModuleNotFoundError:
                pass

    @property
    def command_list(self):
        return "\n".join(self._command_list)

    def process_request(self, url_path, update):

        # Root URL
        if url_path == '' or url_path == '/':
            logger.info("Reply with salute.")
            return "I'm fjfnaranjo's bot."

        # Healt check URL
        elif url_path == '/ping':
            logger.info("Reply with pong.")
            return 'pong'

        # Register webhook request URL
        elif url_path == ('/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook'))):
            self.bot.set_webhook(url=self.webhook_url)
            logger.info("Reply with ok to register_webhook.")
            return 'ok'

        # Register webhook request URL (using self signed cert)
        elif url_path == ('/' + '/'.join((BOT_WEBHOOK_TOKEN, 'register_webhook_self'))):
            self.bot.set_webhook(
                url=self.webhook_url, certificate=open('/botcert/YOURPUBLIC.pem', 'rb')
            )
            logger.info("Reply with ok to register_webhook_self.")
            return 'ok (self)'

        # Don't allow other URLs unless preceded by token
        elif url_path != '/' + BOT_WEBHOOK_TOKEN:
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
        try:
            logger.debug("Dispatch update to library.")
            self.dispatcher.process_update(Update.de_json(update_json, self.bot))
        except Exception as e:
            logger.info("Error inside the framework raised by the dispatcher.")
            raise BotFrameworkError("Error in bot framework.") from e

        return 'ok'


bot = Bot()
