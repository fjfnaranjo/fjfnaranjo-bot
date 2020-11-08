from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, Update
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram.ext import ConversationHandler as ConversationHandler
from telegram.ext import DispatcherHandlerStop, Filters, Handler, MessageHandler
from telegram.ext.dispatcher import DEFAULT_GROUP

from fjfnaranjobot.auth import User, friends, get_owner_id
from fjfnaranjobot.common import SORRY_TEXT
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)
ALL, ONLY_REAL, ONLY_OWNER, ONLY_FRIENDS = range(4)


class BotCommandError(Exception):
    pass


class AnyHandler(Handler):
    def check_update(self, update):
        if (
            Filters.group(update)
            and hasattr(update, "message")
            and Filters.entity(MessageEntity.MENTION).filter(update.message)
        ):
            return update
        if Filters.private(update):
            return update
        return None


def _store_update_context(f):
    @wraps(f)
    def wrapper(instance, update, context):
        instance.update, instance.context = update, context
        return f(instance)

    return wrapper


class Command:
    group = DEFAULT_GROUP
    permissions = ONLY_REAL
    allow_groups = False

    def __init__(self):
        self.update = None
        self.context = None

    def __str__(self):
        return f"{self.__class__.__name__}"

    @staticmethod
    def extract_commands(handler):
        commands = []
        if isinstance(handler, ConversationHandler):
            for entry_point in handler.entry_points:
                for command in Command.extract_commands(entry_point):
                    commands.append(command)
        else:
            if isinstance(handler, CommandHandler):
                for command in handler.command:
                    commands.append(command)
            elif isinstance(handler, AnyHandler):
                commands.append("<any>")
            else:
                commands.append("<unknown command>")
        return commands

    def log_handler(self, group, handler):
        commands = Command.extract_commands(handler)
        for command in commands:
            logger.debug(
                f"New handler for {command}"
                f" created by {self} command"
                f" in group {group}."
            )

    @property
    def handlers(self):
        return []

    def crop_update_text(self):
        message = getattr(self.update, "message", None)
        if message is not None:
            text = getattr(message, "text", None)
            if text is not None:
                if len(text) > 10:
                    text = text[:10] + " (cropped to 10 chars)"
                return text
            else:
                return "<empty>"
        else:
            return "<unknown>"

    def user_is_real(self):
        user = self.update.effective_user
        update_text = self.crop_update_text()
        if user is None:
            logger.warning(
                "Message received with no user"
                f" trying to access an ONLY_REAL command."
                f" Message text: {update_text} ."
            )
            return False
        if user.is_bot:
            logger.warning(
                "Message received from"
                f" bot with username {user.username} and id {user.id}"
                f" trying to access an ONLY_REAL command."
                f" Message text: {update_text} ."
            )
            return False
        return True

    def user_is_owner(self):
        owner_id = get_owner_id()
        user = self.update.effective_user
        update_text = self.crop_update_text()
        if owner_id is None or user.id != owner_id:
            logger.warning(
                "Message received from"
                f" user {user.username} with id {user.id}"
                f" trying to access an ONLY_OWNER command."
                f" Message text: {update_text} ."
            )
            return False
        return True

    def user_is_friend(self):
        owner_id = get_owner_id()
        user = self.update.effective_user
        update_text = self.crop_update_text()
        friend = User(user.id, user.username)
        if (owner_id is not None and user.id == owner_id) or friend not in friends:
            logger.warning(
                "Message received from"
                f" user {user.username} with id {user.id}"
                f" trying to access an ONLY_FRIENDS command."
                f" Message text: {update_text} ."
            )
            return False
        return True

    def check_and_remove_bot_mention(self):
        if hasattr(self.update, "message"):
            bot_mention = "@" + self.context.bot.username
            mentions = self.update.message.parse_entities(MessageEntity.MENTION)
            mentions_keys = list(mentions.keys())
            if (
                len(mentions_keys) == 1
                and mentions[mentions_keys[0]] == bot_mention
                and self.update.message.text.find(bot_mention) == 0
            ):
                self.update.message.text = self.update.message.text.replace(
                    bot_mention, ""
                ).lstrip()
                return True
        return False

    def handle_command(self):
        pass

    @_store_update_context
    def entrypoint(self):
        bot_mentioned = self.check_and_remove_bot_mention()

        if (
            (not self.allow_groups and Filters.group(self.update))
            or (self.allow_groups and Filters.group(self.update) and not bot_mentioned)
            or (self.permissions == ONLY_REAL and not self.user_is_real())
            or (
                self.permissions == ONLY_OWNER
                and (not self.user_is_real() or not self.user_is_owner())
            )
            or (
                self.permissions == ONLY_FRIENDS
                and (not self.user_is_real() or not self.user_is_friend())
            )
        ):
            return

        logger.info(f"Handler for {self} command entered.")
        self.handle_command()
        logger.debug(f"Handler for {self} command exited.")
        raise DispatcherHandlerStop()

    def reply(self, *args, **kwargs):
        return self.update.message.reply_text(*args, **kwargs)


class AnyHandlerMixin(Command):
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                AnyHandler(
                    self.entrypoint,
                ),
            )
        ]
        return super().handlers + new_handlers


class CommandHandlerMixin(Command):
    command_name = None

    @property
    def handlers(self):
        if self.command_name is None:
            raise BotCommandError(f"Command name not defined for {self}")
        new_handlers = [
            (
                self.group,
                CommandHandler(
                    self.command_name,
                    self.entrypoint,
                    filters=Filters.command,
                ),
            )
        ]
        return super().handlers + new_handlers


class ConversationHandlerMixin(Command):
    START = 999  # TODO: Magic number

    command_name = None
    states = {}
    initial_text = "Conversation"
    fallbacks = {}
    remembered_keys = []

    @property
    def handlers(self):
        if self.command_name is None:
            raise BotCommandError(f"Conversation command name not defined for {self}")
        new_handlers = [
            (
                self.group,
                ConversationHandler(
                    [CommandHandler(self.command_name, self.entrypoint)],
                    self.states,
                    [AnyHandler(self.fallback)],
                ),
            )
        ]
        return super().handlers + new_handlers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = {
            self.START: [AnyHandler(self._initial)],
        }

    @_store_update_context
    def _initial(self):
        pass

    def handle_command(self):
        logger.debug(f"Conversation '{self}' started.")
        reply_markup = None
        conversation_message = self.reply(
            self.initial_text,
            reply_markup=reply_markup,
        )
        self.remember("chat_id", conversation_message.chat.id)
        self.remember("message_id", conversation_message.message_id)
        if len(self.states) == 1 and self.START in self.states:
            self.end()

    @_store_update_context
    def fallback(self):
        logger.info(f"Conversation {self} fallback handler started.")
        conversation_message = self.reply("Ups!")
        self.remember("chat_id", conversation_message.chat.id)
        self.remember("message_id", conversation_message.message_id)
        self.end()

    def edit_message(self, text):
        self.context.bot.send_message(self.context.chat_data["chat_id"], text)

    def remember(self, key, value):
        self.remembered_keys.append(key)
        self.context.chat_data[key] = value

    def clean(self):
        self.context.bot.delete_message(
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
        )
        for key in self.remembered_keys:
            if key in self.context.chat_data:
                del self.context.chat_data[key]

    def end(self):
        logger.debug(f"Ending '{self}' conversation.")
        self.context.bot.send_message(self.context.chat_data["chat_id"], "Ok.")
        self.clean()
        return ConversationHandler.END

    @property
    def cancel_markup(self):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="cancel")]]
        )

    @property
    def cancel_inlines(self):
        return {"cancel": self.end}

    def actions_cancel_inlines(self, actions):
        return {
            **self.cancel_inlines,
            **{key: getattr(self, value) for key, value in actions},
        }

    @staticmethod
    def inlines_proxy(inlines):
        def inline_handler_function(update, context):
            logger.debug("Received inline selection.")
            query = update.callback_query.data
            logger.debug(f"Inline selection was '{query}'.")
            if query in inlines:
                return inlines[query](update, context)
            else:
                raise ValueError(f"No valid handlers for query '{query}'.")

        return inline_handler_function


class BotCommand(Command):
    description = ""
    is_prod_command = False
    is_dev_command = True


class Sorry(BotCommand, AnyHandlerMixin):
    group = 999  # TODO: Magic number
    allow_groups = True

    def handle_command(self):
        logger.debug("Sending 'sorry' back to the user.")
        self.reply(SORRY_TEXT)
