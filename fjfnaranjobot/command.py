from telegram import MessageEntity, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    DispatcherHandlerStop,
    Filters,
    Handler,
    MessageHandler,
    StringCommandHandler,
)
from telegram.ext.dispatcher import DEFAULT_GROUP

from fjfnaranjobot.auth import User, friends, get_owner_id
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)
ALL, ONLY_REAL, ONLY_OWNER, ONLY_FRIENDS = range(4)


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


class Command:
    name = ""
    group = DEFAULT_GROUP
    permissions = ONLY_REAL
    allow_groups = False

    def __init__(self):
        self.update = None
        self.context = None

    @staticmethod
    def extract_commands(handler):
        commands = []
        if isinstance(handler, ConversationHandler):
            for entry_point in handler.entry_points:
                commands.append(Command.extract_commands(entry_point))
        else:
            if isinstance(handler, CommandHandler):
                for command in handler.command:
                    commands.append(command)
            elif isinstance(handler, StringCommandHandler):
                commands.append(handler.command)
            elif isinstance(handler, MessageHandler):
                commands.append("<message>")
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
                f" created by {self.__class__.__name__} command"
                f" in group {group}."
            )

    @property
    def handlers(self):
        return []

    def clean(self):
        pass

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

    def entrypoint(self, update, context):
        self.update, self.context = update, context

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
            self.clean()
            return

        logger.info(f"Handler for {self.__class__.__name__} command entered.")
        self.handle_command()
        logger.debug(f"Handler for {self.__class__.__name__} command exited.")
        self.stop()

    def stop(self):
        self.clean()
        raise DispatcherHandlerStop()

    def reply(self, text):
        self.update.message.reply_text(text)


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
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                CommandHandler(
                    self.name,
                    self.entrypoint,
                    filters=Filters.command,
                ),
            )
        ]
        return super().handlers + new_handlers


class TextHandlerMixin(Command):
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                MessageHandler(
                    Filters.text,
                    self.entrypoint,
                ),
            )
        ]
        return super().handlers + new_handlers


class BotCommand(Command):
    description = ""
    is_prod_command = False
    is_dev_command = False

    # TODO: Remove proxy
    @property
    def prod_command(self):
        return self.name

    @property
    def dev_command(self):
        return self.name
