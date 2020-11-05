from telegram import MessageEntity
from telegram.ext import MessageHandler, Filters, DispatcherHandlerStop
from telegram.ext.dispatcher import DEFAULT_GROUP
from telegram.ext.commandhandler import CommandHandler


from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Command:
    name = ''
    group = DEFAULT_GROUP

    def __init__(self):
        self.update = None
        self.context = None

    def reply(self, text):
        self.update.message.reply_text(text)

    # TODO: Consider reporting hadlers registration in children of this def
    @property
    def handlers(self):
        return []

    def handle_command(self):
        pass


class CommandHandlerMixin(Command):
    @property
    def handlers(self):
        return super().handlers + [(self.group, CommandHandler(
            self.name, self.entrypoint,
        ))]

    def entrypoint(self, update, context):
        self.update, self.context = update, context

        logger.info(f"Command {self.__class__.__name__} received.")
        self.handle_command()
        logger.debug(f"Command {self.__class__.__name__} processed.")
        raise DispatcherHandlerStop()


class MessageCommandHandlerMixin(CommandHandlerMixin):
    @property
    def handlers(self):
        return super(CommandHandlerMixin, self).handlers + [(self.group, MessageHandler(
            Filters.private & Filters.text, self.entrypoint,
        ))]

    def entrypoint(self, update, context):
        self.update, self.context = update, context

        logger.info(f"Message {self.__class__.__name__} received.")
        self.handle_command()
        logger.debug(f"Message {self.__class__.__name__} processed.")
        raise DispatcherHandlerStop()


class GroupCommandHandlerMixin(Command):
    @property
    def handlers(self):
        return super().handlers + [(self.group, CommandHandler(
            self.name, self.group_entrypoint, filters=Filters.group,
        ))]

    def group_entrypoint(self, update, context):
        self.update, self.context = update, context

        logger.info(f"Group command {self.__class__.__name__} received.")

        bot_mention = "@" + context.bot.username
        mentions = update.message.parse_entities(MessageEntity.MENTION)
        mentions_keys = list(mentions.keys())
        if (
            len(mentions_keys) == 1
            and mentions[mentions_keys[0]] == bot_mention
            and update.message.text.find(bot_mention) == 0
        ):
            update.message.text = \
                update.message.text.replace(bot_mention, "").strip()

        self.handle_group_command()
        logger.debug(f"Group command {self.__class__.__name__} processed.")
        raise DispatcherHandlerStop()

    def handle_group_command(self):
        return self.handle_command()


class GroupMessageCommandHandlerMixin(GroupCommandHandlerMixin):
    @property
    def handlers(self):
        return super(GroupCommandHandlerMixin, self).handlers + [(self.group, MessageHandler(
            Filters.group
            & Filters.text
            & Filters.entity(MessageEntity.MENTION),
            self.group_entrypoint,
        ))]

    def group_entrypoint(self, update, context):
        self.update, self.context = update, context

        logger.info(f"Group message {self.__class__.__name__} received.")
        self.handle_group_command()
        logger.debug(f"Group message {self.__class__.__name__} processed.")
        raise DispatcherHandlerStop()


class BotCommand(Command):
    description = ''
    is_prod_command = False
    is_dev_command = False

    # TODO: Remove proxy
    @property
    def prod_command(self):
        return self.name

    @property
    def dev_command(self):
        return self.name
