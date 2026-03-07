"""Commands module.

This module abstracts the python-telegram-bot library and contains the basic
tools to define new bot commands. Each of the bot components use the definitions
in this file to add commands to the bot.

Commands intended for internal use should inherit from the Command class but
commands that will appear in the bot commands list (in Telegram) should inherit
from BotCommand.

Check each class docstring for details about its required paramenters.

Any command will need a 'command handler mixin'. This mixins connect the command
to the updates handlers in python-telegram-bot . See each *Mixin docstring.
"""

from contextlib import contextmanager
from functools import wraps
from math import ceil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import (
    ApplicationHandlerStop,
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
)
from telegram.ext import ConversationHandler as ConversationHandler
from telegram.ext import MessageHandler

# TODO: Find a different way to allow a default group in commands
from telegram.ext._application import DEFAULT_GROUP
from telegram.ext.filters import COMMAND, CONTACT, TEXT, ChatType, Entity

from fjfnaranjobot.auth import User, friends, get_owner_id
from fjfnaranjobot.common import (
    CANCEL_CAPTION,
    DEFAULT_PAGE_SIZE,
    NEXT_PAGE_CAPTION,
    RESTART_PAGINATOR_CAPTION,
    quote_value_for_log,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class BotCommandError(RuntimeError):
    pass


# TODO: Test (and consider adding _ in lots of members...)
# TODO: Instead of requiring class+mixin we can create the pairs ourselves
#       Move this classes to a "base" module, and we can have here
#       Command(CommandHandlerMixin, BotCommand)
#       Conversation(ConversationHandlerMixin, BotCommand)
#       ...
class Command:
    """Base command for all the bot commands.

    Parameters:
      - dispatcher_group: python-telegram-bot priority group. See 'group' in
                          telegram.ext.dispatcher.Dispatcher.add_handler() .
      - permissions: Who can use this command (anyone, non-bot users,
                     friends or the owner).
      - allow_chats: If the command will be allowed in group chats.
    """

    class PermissionsEnum:
        ALL, ONLY_REAL, ONLY_OWNER, ONLY_FRIENDS = range(4)

    dispatcher_group = DEFAULT_GROUP
    permissions = PermissionsEnum.ONLY_REAL
    allow_chats = False

    def __init__(self):
        self.update = None
        self.context = None

    def __str__(self):
        return f"{self.__class__.__name__}"

    # TODO: This depends on classes down the hierarchy. Use cooperation.
    @staticmethod
    def extract_commands(handler):
        commands = []
        if isinstance(handler, ConversationHandler):
            for entry_point in handler.entry_points:
                for command in Command.extract_commands(entry_point):
                    commands.append(command)
        else:
            if isinstance(handler, CommandHandler):
                for command in handler.commands:
                    commands.append(command)
            elif isinstance(handler, AnyHandler):
                commands.append("<any>")
            else:
                commands.append("<unknown command>")
        return commands

    def log_handler(self, dispatcher_group, handler):
        commands = Command.extract_commands(handler)
        for command in commands:
            logger.debug(
                f"New handler for {command}"
                f" created by {self} command"
                f" in dispatcher group {dispatcher_group}."
            )

    @property
    def handlers(self):
        return []

    def crop_update_text(self):
        message = getattr(self.update, "message", None)
        if message is not None:
            text = getattr(message, "text", None)
            if text is not None:
                return quote_value_for_log(text)
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
                " trying to access an ONLY_REAL command."
                f" Message text: {update_text} ."
            )
            return False
        if user.is_bot:
            logger.warning(
                "Message received from"
                f" bot with username {user.username} and id {user.id}"
                " trying to access an ONLY_REAL command."
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
                " trying to access an ONLY_OWNER command."
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
                " trying to access an ONLY_FRIENDS command."
                f" Message text: {update_text} ."
            )
            return False
        return True

    # TODO: If this uses hasattr it belongs outside the class or should be better deisnged
    def _check_and_remove_bot_mention(self):
        if hasattr(self.update, "message") and self.update.message is not None:
            bot_mention = "@" + self.context.bot.username
            mentions = self.update.message.parse_entities(MessageEntity.MENTION)
            commands = self.update.message.parse_entities(MessageEntity.BOT_COMMAND)
            mentions_keys = list(mentions.keys())
            commands_keys = list(commands.keys())
            if (
                len(mentions_keys) == 1
                and mentions[mentions_keys[0]] == bot_mention
                and (
                    self.update.message.text.find(bot_mention) == 0
                    or self.update.message.text.find(bot_mention)
                    == len(self.update.message.text) - len(bot_mention)
                )
            ) or (
                len(commands_keys) == 1
                and hasattr(self, "command_name")
                and self.command_name is not None
                and commands[commands_keys[0]] == "/" + self.command_name + bot_mention
            ):
                self.update.message.text = self.update.message.text.replace(
                    bot_mention, ""
                ).lstrip()
                return True

        return False

    # TODO: Log security warnings
    def filter_command(self):
        bot_mentioned = self._check_and_remove_bot_mention()

        return (
            False
            if (
                (not self.allow_chats and ChatType.GROUPS.check_update(self.update))
                or (
                    self.allow_chats
                    and ChatType.GROUPS.check_update(self.update)
                    and not bot_mentioned
                )
                or (
                    self.permissions == Command.PermissionsEnum.ONLY_REAL
                    and not self.user_is_real()
                )
                or (
                    self.permissions == Command.PermissionsEnum.ONLY_OWNER
                    and (not self.user_is_real() or not self.user_is_owner())
                )
                or (
                    self.permissions == Command.PermissionsEnum.ONLY_FRIENDS
                    and (not self.user_is_real() or not self.user_is_friend())
                )
            )
            else True
        )

    async def entrypoint(self):
        raise NotImplementedError(f"Command {self} doesn't have an entrypoint.")

    async def handle_command(self, update, context):
        self.update = update
        self.context = context
        if not self.filter_command():
            return
        logger.info(f"Calling command entrypoint in {self}...")
        await self.entrypoint()
        raise ApplicationHandlerStop()

    async def reply(self, *args, **kwargs):
        if hasattr(self.update, "message") and self.update.message is not None:
            return await self.update.message.reply_text(*args, **kwargs)
        else:
            return await self.context.bot.send_message(
                self.update.effective_chat.id, *args, **kwargs
            )


class AnyHandler(BaseHandler):
    """Extra python-telegram-bot handler to select any update."""

    def check_update(self, update):
        if (
            ChatType.GROUPS.check_update(update)
            and hasattr(update, "message")
            and update.message is not None
            and Entity(MessageEntity.MENTION).filter(update.message)
        ):
            return update
        if ChatType.PRIVATE.check_update(update):
            return update
        return None


class AnyHandlerMixin(Command):
    """Mixin to handle any command."""

    @property
    def handlers(self):
        new_handlers = [
            (
                self.dispatcher_group,
                AnyHandler(
                    self.handle_command,
                ),
                self.__class__.__name__,
            )
        ]
        return super().handlers + new_handlers


# TODO: Remove dev/prod distinction
class BotCommand(Command):
    """Command notified to BotFather.

    Inherit from this base instead of Command to notify the command as a bot
    command. This will make the command available as an option in Telegram's
    conversations.

    Parameters:
      - command_name: Name of the command used after the / .
      - description: Little text used in the Telegram commands interface.
      - is_(dev|prod)_command: Filter to determine if the commands is meant to
                               be exposed in the dev/prod versions of the bot.
    """

    command_name = None
    description = ""
    is_dev_command = True
    is_prod_command = False

    def __init__(self):
        super().__init__()
        if self.command_name is None:
            raise BotCommandError(f"Command name not defined for {self}.")


class CommandHandlerMixin(BotCommand):
    """Mixin to handle simple and single commands."""

    @property
    def handlers(self):
        new_handlers = [
            (
                self.dispatcher_group,
                CommandHandler(
                    self.command_name,
                    self.handle_command,
                    filters=COMMAND,
                ),
                self.__class__.__name__,
            )
        ]
        return super().handlers + new_handlers


class ConversationHandlerMixin(BotCommand):
    """Mixin to handle python-telegram-bot conversation."""

    START = 0

    always_cancelable = True

    clean_chat_data_keys = []
    clean_user_data_keys = []
    clean_bot_data_keys = []

    def __init__(self):
        super().__init__()
        self.states = {}
        self.build_states(self.state_builder)
        if self.START not in self.states.keys():
            raise BotCommandError(f"Conversation START state not defined for {self}.")
        self._clear_context()

    def build_states(self, builder):
        raise NotImplementedError(
            f"Conversation states builder not implemented for {self}."
        )

    @contextmanager
    def state_builder(self, state_id):
        new_state = State()
        new_state.id = state_id
        if self.always_cancelable:
            new_state.cancelable = True
        yield new_state
        self.states[state_id] = new_state

    @property
    def handlers(self):
        new_handlers = [
            (
                self.dispatcher_group,
                ConversationHandler(
                    [CommandHandler(self.command_name, self.start_conversation)],
                    self.states_handlers,
                    [AnyHandler(self.fallback)],
                ),
                self.__class__.__name__,
            )
        ]
        return super().handlers + new_handlers

    @property
    def states_handlers(self):
        states_handlers = {}  # state_id: [handler, ...]

        for state_id in self.states:
            states_handlers[state_id] = []
            state = self.states[state_id]
            if state.cancelable:
                states_handlers[state_id].append(
                    CallbackQueryHandler(
                        self.cancel_handler,
                        pattern=rf"^cancel$",
                    )
                )
            if state.text_handler:
                states_handlers[state_id].append(
                    MessageHandler(
                        TEXT,
                        self.text_handler(
                            getattr(self, f"{state.text_handler}_handler")
                        ),
                    )
                )
            if state.contact_handler:
                states_handlers[state_id].append(
                    MessageHandler(
                        CONTACT,
                        self.contact_handler(
                            getattr(self, f"{state.contact_handler}_handler")
                        ),
                    )
                )

            for inline in state.inlines:
                states_handlers[state_id].append(
                    CallbackQueryHandler(
                        self.inline_handler(getattr(self, f"{inline.handler}_handler")),
                        pattern=rf"^{inline.handler}$",
                    )
                )

            for jump in state.jumps:
                states_handlers[state_id].append(
                    CallbackQueryHandler(
                        self.jump_handler,
                        pattern=rf"^jump-.*$",
                    )
                )

            if state.paginator is not None:
                states_handlers[state_id].append(
                    CallbackQueryHandler(
                        self.paginator_handler, pattern=rf"^pag-{state_id}-.*$"
                    )
                )

        return states_handlers

    async def start_conversation(self, update, context):
        self.update = update
        self.context = context
        if not self.filter_command():
            return
        logger.info(f"Starting conversation {self}...")
        conversation_message = await self.reply(
            (
                self.states[self.START].message
                if self.states[self.START].message is not None
                else f"Starting conversation '{self.command_name}'."
            ),
            reply_markup=self.markup_from_state(self.START),
        )
        self.context.chat_data["chat_id"] = conversation_message.chat.id
        self.context.chat_data["message_id"] = conversation_message.message_id
        raise ApplicationHandlerStop(self.START)

    async def fallback(self, update, context):
        self.update = update
        self.context = context
        warning_text = f"Conversation {self} fallback handler reached."
        try:
            query_data = self.update.callback_query.data
            quoted = quote_value_for_log(query_data)
            warning_text += f" Callback query data was {quoted}."
        except AttributeError:
            pass
        logger.warning(warning_text)
        await self.end("Ups!")

    async def edit_message(self, text, reply_markup=None):
        await self.context.bot.edit_message_text(
            text,
            self.context.chat_data.get("chat_id"),
            self.context.chat_data.get("message_id"),
            reply_markup=reply_markup,
        )

    def _clear_context(self):
        if self.context is not None:
            for state in self.states:
                current_page_key = f"pag-{state}-current-page"
                if current_page_key in self.context.chat_data:
                    del self.context.chat_data[current_page_key]
                last_ids_key = f"pag-{state}-last-ids"
                if last_ids_key in self.context.chat_data:
                    del self.context.chat_data[last_ids_key]

            for key in self.clean_chat_data_keys:
                if key in self.context.chat_data:
                    del self.context.chat_data[key]
            for key in self.clean_user_data_keys:
                if key in self.context.user_data:
                    del self.context.user_data[key]
            for key in self.clean_bot_data_keys:
                if key in self.context.bot_data:
                    del self.context.bot_data[key]

    async def _clean(self):
        if self.context is not None:
            if "chat_id" in self.context.chat_data:
                await self.context.bot.delete_message(
                    self.context.chat_data.pop("chat_id"),
                    self.context.chat_data.pop("message_id"),
                )
        self._clear_context()

    async def end(self, end_message="Ok."):
        if end_message is not None:
            await self.reply(end_message)
        await self._clean()
        logger.info(f"{self} conversation ends.")
        raise ApplicationHandlerStop(ConversationHandler.END)

    # TODO: Consider default state for next state (IIII)
    # TODO: Also, consider the state inlines for next states and markup
    # Move state to second position and use as kwarg
    # TODO: Command users depend on this to create 'next' markups (II)
    async def next(self, next_state_id, new_message=None, reply_markup=None):
        has_to_edit = False
        try:
            new_state = self.states[next_state_id]
        except KeyError:
            raise BotCommandError(
                f"State ID {next_state_id} doesn't exists for {self}."
            )

        if new_message is not None:
            has_to_edit = True
        elif new_state.message is not None:
            has_to_edit = True
            new_message = new_state.message

        if reply_markup is not None:
            has_to_edit = True
        else:
            reply_markup = self.markup_from_state(next_state_id)

        if has_to_edit:
            await self.edit_message(new_message, reply_markup=reply_markup)

        logger.debug(
            f"{self} conversation changes state to {next_state_id} and stops the dispatcher."
        )

        raise ApplicationHandlerStop(next_state_id)

    async def cancel_handler(self, update, context):
        self.update = update
        self.context = context
        logger.info(f"Cancelling conversation {self}...")
        await self.end("Ok.")

    def text_handler(self, handler):
        async def _text_handler_function(update, context):
            self.update = update
            self.context = context
            return await handler(self.update.message.text)

        return _text_handler_function

    def contact_handler(self, handler):
        async def _contact_handler_function(update, context):
            self.update = update
            self.context = context
            contact = self.update.message.contact
            if contact.user_id is None:
                logger.debug("Received a contact without a Telegram ID.")
            else:
                return await handler(self.update.message.contact)

        return _contact_handler_function

    def inline_handler(self, handler):
        async def _inline_handler_function(update, context):
            self.update = update
            self.context = context
            query = update.callback_query.data
            if query != "cancel":
                logger.info(
                    f"Continuing conversation {self} after receiving inline selection '{query}'..."
                )
            return await handler()

        return _inline_handler_function

    async def jump_handler(self, update, context):
        self.update = update
        self.context = context
        query = update.callback_query.data
        # 'jump-0' => 0
        state_id = int(query[5:])
        logger.info(f"Continuing conversation {self} jumping to state {state_id}...")
        await self.next(state_id)

    async def paginator_handler(self, update, context):
        self.update = update
        self.context = context

        query = update.callback_query.data
        # 'pag-0-4' => (0, "4")
        # 'pag-0-next' => (0, "next")
        state_id, selection = (
            int(query[4 : query.find("-", 4)]),
            query[query.find("-", 4) + 1 :],
        )

        paginator = self.states[state_id].paginator
        if paginator.count == 0:
            await self.end(self.empty_message)

        current_page = self.context.chat_data.pop(f"pag-{state_id}-current-page", 0)

        if selection == "next":
            logger.info(
                f"Handling next page requested for paginator {state_id}"
                f" in conversation {self} with last page {current_page}..."
            )

            if paginator.has_next_page(current_page):
                current_page += 1
            else:
                current_page = 0
            self.context.chat_data[f"pag-{state_id}-current-page"] = current_page

            await self.next(state_id)

        else:
            logger.info(
                f"Handling selection {selection}"
                f" received for paginator {state_id}"
                f" in conversation {self}..."
            )

            last_ids = self.context.chat_data.pop(f"pag-{state_id}-last-ids")
            current_ids = ",".join(
                str(paginator.id_func(item))
                for item in paginator.items_in_page(current_page)
            )
            if not last_ids == current_ids:
                logger.info(
                    f"Resetting paginator {state_id}" f" in conversation {self}..."
                )
                self.context.chat_data[f"pag-{state_id}-current-page"] = 0
                await self.next(state_id)

            # TODO: Don't impose _handler sufix to the framework user
            await getattr(self, paginator.handler + "_handler")(
                paginator.iterable.get_by_id(selection)
            )

    def markup_from_state(self, state_id):
        state = self.states[state_id]

        markup = []

        inlines_row = list(
            [
                InlineKeyboardButton(inline.caption, callback_data=inline.handler)
                for inline in state.inlines
            ]
            + [
                InlineKeyboardButton(
                    jump.caption, callback_data=f"jump-{jump.state_id}"
                )
                for jump in state.jumps
            ]
        )
        if inlines_row:
            markup.append(inlines_row)

        if state.paginator is not None:
            rows = self.markup_from_state_paginator(state)
            for row in rows:
                markup.append(row)

        if state.cancelable:
            markup.append(
                [InlineKeyboardButton(CANCEL_CAPTION, callback_data="cancel")]
            )

        return InlineKeyboardMarkup(markup) if markup else None

    def markup_from_state_paginator(self, state):
        current_page = self.context.chat_data.get(f"pag-{state.id}-current-page", 0)
        rows = []
        paginator = state.paginator
        items = paginator.items_in_page(current_page)

        self.context.chat_data[f"pag-{state.id}-last-ids"] = ",".join(
            str(paginator.id_func(item)) for item in items
        )

        for item in items:
            rows.append(
                [
                    InlineKeyboardButton(
                        paginator.caption_func(item),
                        callback_data=f"pag-{state.id}-{paginator.id_func(item)}",
                    )
                ]
            )
        if paginator.has_pages:
            rows.append(
                [
                    InlineKeyboardButton(
                        (
                            NEXT_PAGE_CAPTION
                            if paginator.has_next_page(current_page)
                            else RESTART_PAGINATOR_CAPTION
                        ),
                        callback_data=f"pag-{state.id}-next",
                    )
                ]
            )
        return rows


# TODO: Consider default state for next state (III)
# add_inline_default_next()?
# TODO: Reserve certain names in inlines: like 'pag-[0-9]+-(([0-9]+)|(next))'
# or 'paginator_proxy'
# TODO: In fact, we can create the inlines ourselves
# TODO: NamedTuples or classes for members with dicts
# TODO: Don't impose _handler sufix to the framework user
class Inline:
    def __init__(self, caption, handler):
        self.caption = caption
        self.handler = handler


class Jump:
    def __init__(self, caption, state_id):
        self.caption = caption
        self.state_id = state_id


class Paginator:
    def __init__(
        self,
        iterable,
        id_func,
        caption_func,
        empty_message,
        handler,
        page_size=DEFAULT_PAGE_SIZE,
    ):
        self.iterable = iterable
        self.id_func = id_func
        self.caption_func = caption_func
        self.empty_message = empty_message
        self.handler = handler
        self.page_size = page_size

        if page_size is None or not self.page_size > 0:
            raise BotCommandError("Paginator page_size must be greater than 0.")

    @property
    def count(self):
        return len(self.iterable)

    @property
    def has_pages(self):
        return self.count > self.page_size

    def has_next_page(self, page):
        return (page + 2) <= ceil(self.count / self.page_size)

    def items_in_page(self, page):
        page_start = page * self.page_size
        item_count_in_page = (
            self.page_size if self.has_next_page(page) else self.count - page_start
        )
        sorted_items = list(self.iterable.sorted())
        return sorted_items[page_start : page_start + item_count_in_page]


class State:
    def __init__(self):
        self.id = None
        self.cancelable = None
        self.message = None
        self.text_handler = None
        self.contact_handler = None
        self.inlines = []
        self.jumps = []
        self.paginator = None

    def add_jump(self, caption, state_id):
        self.jumps.append(Jump(caption, state_id))

    def add_inline(self, caption, handler):
        self.inlines.append(Inline(caption, handler))

    def add_paginator(
        self,
        iterable,
        id_func,
        caption_func,
        empty_message,
        handler,
        page_size=DEFAULT_PAGE_SIZE,
    ):
        self.paginator = Paginator(
            iterable,
            id_func,
            caption_func,
            empty_message,
            handler,
            page_size,
        )
