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

from fjfnaranjobot.auth import (
    User,
    _report_bot,
    _report_no_user,
    _report_user,
    friends,
    get_owner_id,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)
ALL, ONLY_REAL, ONLY_OWNER, ONLY_FRIENDS = range(4)


class AnyHandler(Handler):
    def check_update(self, update):
        return update


class Command:
    name = ""
    group = DEFAULT_GROUP
    permissions = ALL

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

    @staticmethod
    def log_handlers_info(handlers, command_class):
        for group, handler in handlers:
            commands = Command.extract_commands(handler)
            for command in commands:
                logger.debug(
                    f"New handler for {command}"
                    f" created by {command_class.__name__} command"
                    f" in group {group}."
                )

    @property
    def handlers(self):
        return []

    def clean(self):
        pass

    def stop(self):
        self.clean()
        raise DispatcherHandlerStop()

    def user_is_real(self):
        user = self.update.effective_user
        if user is None:
            _report_no_user(self.update, "only_real")
            self.clean()
            return False
        if user.is_bot:
            _report_bot(self.update, user, "only_real")
            self.clean()
            return False
        return True

    def user_is_owner(self):
        if not self.user_is_real():
            self.clean()
            return False
        owner_id = get_owner_id()
        user = self.update.effective_user
        if owner_id is None or user.id != owner_id:
            _report_user(self.update, user, "only_owner")
            self.clean()
            return False
        return True

    def user_is_friend(self):
        if not self.user_is_real():
            self.clean()
            return False
        owner_id = get_owner_id()
        user = self.update.effective_user
        friend = User(user.id, user.username)
        if (owner_id is not None and user.id == owner_id) or friend not in friends:
            _report_user(self.update, user, "only_friends")
            self.clean()
            return False
        return True

    def handle_command(self):
        pass

    def entrypoint(self, update, context):
        self.update, self.context = update, context

        if self.permissions == ONLY_REAL:
            if not self.user_is_real():
                return
        if self.permissions == ONLY_OWNER:
            if not self.user_is_owner():
                return
        if self.permissions == ONLY_FRIENDS:
            if not self.user_is_friend():
                return

        logger.info(f"Handler for {self.__class__.__name__} command entered.")
        self.handle_command()
        logger.debug(f"Handler for {self.__class__.__name__} command exited.")
        self.stop()

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
        self.log_handlers_info(new_handlers, self.__class__)
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
                    filters=Filters.private & Filters.command,
                ),
            )
        ]
        self.log_handlers_info(new_handlers, self.__class__)
        return super().handlers + new_handlers


class TextHandlerMixin(Command):
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                MessageHandler(
                    Filters.private & Filters.text,
                    self.entrypoint,
                ),
            )
        ]
        self.log_handlers_info(new_handlers, self.__class__)
        return super().handlers + new_handlers


class GroupEntrypointMixin(Command):
    def entrypoint(self, update, context):
        bot_mention = "@" + context.bot.username
        mentions = update.message.parse_entities(MessageEntity.MENTION)
        mentions_keys = list(mentions.keys())
        if (
            len(mentions_keys) == 1
            and mentions[mentions_keys[0]] == bot_mention
            and update.message.text.find(bot_mention) == 0
        ):
            update.message.text = update.message.text.replace(bot_mention, "").strip()

        return super().entrypoint(update, context)


class GroupCommandHandlerMixin(GroupEntrypointMixin, Command):
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                CommandHandler(
                    self.name,
                    self.entrypoint,
                    filters=Filters.group
                    & Filters.command
                    & Filters.entity(MessageEntity.MENTION),
                ),
            )
        ]
        self.log_handlers_info(new_handlers, self.__class__)
        return super().handlers + new_handlers


class GroupTextHandlerMixin(GroupEntrypointMixin, Command):
    @property
    def handlers(self):
        new_handlers = [
            (
                self.group,
                MessageHandler(
                    Filters.group
                    & Filters.text
                    & Filters.entity(MessageEntity.MENTION),
                    self.entrypoint,
                ),
            )
        ]
        self.log_handlers_info(new_handlers, self.__class__)
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
