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

from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram.ext import ConversationHandler as ConversationHandler
from telegram.ext import DispatcherHandlerStop, Filters, Handler, MessageHandler
from telegram.ext.dispatcher import DEFAULT_GROUP

from fjfnaranjobot.auth import User, friends, get_owner_id
from fjfnaranjobot.common import (
    quote_value_for_log,
    NEXT_PAGE_CAPTION,
    RESTART_PAGINATOR_CAPTION,
    CANCEL_CAPTION,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class BotCommandError(Exception):
    pass


# TODO: Test (and consider adding _ in lots of members...)


# TODO: This probably shoul be removed
def store_update_context(f):
    @wraps(f)
    def store_update_context_wrapper(instance, update, context, *args, **kwargs):
        instance.update = update
        instance.context = context
        return f(instance, *args, **kwargs)

    return store_update_context_wrapper


# TODO: This decorator can be avoided if implementing a text_handler method
def store_update_context_text_command(f, command, query):
    @wraps(f)
    def store_update_context_text_command_wrapper(update, context, *args, **kwargs):
        command.update = update
        command.context = context
        logger.info(
            f"Continuing conversation {command} after receiving text selection '{query}'..."
        )
        return f(*args, **kwargs)

    return store_update_context_text_command_wrapper


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
                (not self.allow_chats and Filters.chat_type.groups(self.update))
                or (
                    self.allow_chats
                    and Filters.chat_type.groups(self.update)
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

    def entrypoint(self):
        raise NotImplementedError()

    @store_update_context
    def handle_command(self):
        if not self.filter_command():
            return
        logger.info(f"Calling command entrypoint in {self}...")
        self.entrypoint()
        raise DispatcherHandlerStop()

    def reply(self, *args, **kwargs):
        if hasattr(self.update, "message") and self.update.message is not None:
            return self.update.message.reply_text(*args, **kwargs)
        else:
            return self.context.bot.send_message(
                self.update.effective_chat.id, *args, **kwargs
            )


class AnyHandler(Handler):
    """Extra python-telegram-bot handler to select any update."""

    def check_update(self, update):
        if (
            Filters.chat_type.groups(update)
            and hasattr(update, "message")
            and update.message is not None
            and Filters.entity(MessageEntity.MENTION).filter(update.message)
        ):
            return update
        if Filters.chat_type.private(update):
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


class BotCommand(Command):
    """Command notified to BotFather.

    Inherit from this base instead of Command to notify the command as a bot
    command. This will make the command available as an option in Telegram's
    conversations.

    Parameters:
      - description: Little text used in the Telegram commands interface.
      - is_(dev|prod)_command: Filter to determine if the commands is meant to
                               be exposed in the dev/prod versions of the bot.
    """

    command_name = None
    description = ""
    is_dev_command = True
    is_prod_command = False


class CommandHandlerMixin(BotCommand):
    """Mixin to handle simple and single commands."""

    @property
    def handlers(self):
        if self.command_name is None:
            raise BotCommandError(f"Command name not defined for {self}")
        new_handlers = [
            (
                self.dispatcher_group,
                CommandHandler(
                    self.command_name,
                    self.handle_command,
                    filters=Filters.command,
                ),
                self.__class__.__name__,
            )
        ]
        return super().handlers + new_handlers


# TODO: Auto insert cancel inline as command option (but allow manual insert) (I)
class ConversationHandlerMixin(BotCommand):
    """Mixin to handle python-telegram-bot conversation."""

    START = 0

    initial_text = "Conversation"
    clean_keys = []

    _remembered_keys = []
    _paginators = {}

    def __init__(self):
        super().__init__()
        if self.command_name is None:
            raise BotCommandError(f"Conversation command name not defined")
        self.states = StateSet(self)
        self.markup = MarkupBuilder()

    @property
    def handlers(self):
        new_handlers = [
            (
                self.dispatcher_group,
                ConversationHandler(
                    [CommandHandler(self.command_name, self.start_conversation)],
                    self.states.graph,
                    [AnyHandler(self.fallback)],
                ),
                self.__class__.__name__,
            )
        ]
        return super().handlers + new_handlers

    @store_update_context
    def start_conversation(self):
        if not self.filter_command():
            return
        logger.info(f"Starting conversation '{self}'...")
        conversation_message = self.reply(
            self.initial_text,
            # TODO: This call should be something like self.states.start_markup()
            reply_markup=self.markup.from_start(
                self.states.inlines,
                self.states.paginators_inline_proxies,
            ),
        )
        self.context_set("chat_id", conversation_message.chat.id)
        self.context_set("message_id", conversation_message.message_id)
        self.next(self.START)

    @store_update_context
    def fallback(self):
        warning_text = f"Conversation {self} fallback handler reached."
        try:
            query_data = self.update.callback_query.data
            warning_text += f" Callback query data was '{query_data}'."
        except AttributeError:
            pass
        logger.warning(warning_text)
        self.end("Ups!")

    def edit_message(self, text, reply_markup=None):
        self.context.bot.edit_message_text(
            text,
            self.context_get("chat_id"),
            self.context_get("message_id"),
            reply_markup=reply_markup,
        )

    def context_set(self, key, value):
        old_value = (
            self.context.chat_data.get(key) if key in self.context.chat_data else None
        )
        if key not in self._remembered_keys:
            self._remembered_keys.append(key)
        self.context.chat_data[key] = value
        return old_value

    def context_exists(self, key):
        return key in self.context.chat_data

    def context_get(self, key, default=None):
        return self.context.chat_data.get(key, default)

    def context_del(self, key):
        old_value = self.context.chat_data[key]
        del self.context.chat_data[key]
        if key in self._remembered_keys:
            self._remembered_keys.remove(key)
        return old_value

    def _clear_context(self):
        for key in self._remembered_keys + self.clean_keys:
            if key in self.context.chat_data:
                del self.context.chat_data[key]

    def _clean(self):
        if self.context_exists("chat_id"):
            self.context.bot.delete_message(
                self.context_get("chat_id"),
                self.context_get("message_id"),
            )
        self._clear_context()

    def end(self, end_message=None):
        if end_message is not None:
            self.reply(end_message)
        self._clean()
        logger.info(f"'{self}' conversation ends.")
        raise DispatcherHandlerStop(ConversationHandler.END)

    # TODO: Consider default state for next state (IIII)
    # Move state to second position and use as kwarg
    # TODO: Command users depend on this to create 'next' markups (II)
    def next(self, state, new_message=None, reply_markup=None):
        if new_message is not None:
            self.edit_message(new_message, reply_markup=reply_markup)
        logger.debug(
            f"'{self}' conversation changes state to {state} and stops the dispatcher."
        )
        raise DispatcherHandlerStop(state)

    def cancel_handler(self):
        logger.info(f"Cancelling conversation '{self}'...")
        return self.end("Ok.")

    def inline_handler(self, handler):
        def _inline_handler_function(update, context):
            self.update = update
            self.context = context
            query = update.callback_query.data
            if query != "cancel":
                logger.info(
                    f"Continuing conversation {self} after receiving inline selection '{query}'..."
                )
            return handler()

        return _inline_handler_function

    def paginator_handler(self):
        def _paginator_handler_function(update, context):
            self.update = update
            self.context = context
            query = update.callback_query.data

            # 'pag-0-4' => ("0", "4")
            paginator, selection = (
                query[4 : query.find("-", 4)],
                query[query.find("-", 4) + 1 :],
            )
            paginator_state = int(paginator)
            next_selected, selected_index = (
                (True, -999) if selection == "next" else (False, int(selection))
            )

            paginator_settings = self.states.paginator_settings(paginator_state)
            get_caption_func = paginator_settings["get_caption_func"]

            page_size = paginator_settings["page_size"]

            sorted_items = list(paginator_settings["iterable"].sorted())
            item_count = len(sorted_items)
            if item_count == 0:
                self.end(paginator_settings["empty_message"])

            offset = self.context_get(f"pag-offset-{paginator}")
            inlines_offset = self.context_get(f"pag-inlines-offset-{paginator}")
            item_offset = offset if offset is not None else 0
            item_count_in_page = min(page_size, item_count - item_offset)

            if not next_selected and selected_index >= item_count_in_page:
                logger.warning(
                    f"Invalid selection '{query}'"
                    f" received for paginator '{paginator}'"
                    f" with offset '{offset}'"
                    f" in conversation {self}."
                )
                raise ValueError(
                    f"No valid handlers for query '{query}'"
                    f" received for paginator '{paginator}'"
                    f" with offset '{offset}'"
                    f" in conversation {self}."
                )

            else:
                logger.info(
                    f"Handling page requested for paginator '{paginator}'"
                    f" in conversation {self} with offset {item_offset}..."
                )

                show_button = None
                if item_count <= page_size:
                    new_offset = 0
                else:
                    pending_pages = (item_count - item_offset) // page_size
                    if pending_pages > 0:
                        show_button = "next"
                        new_offset = item_offset + page_size
                    else:
                        show_button = "restart"
                        new_offset = 0

                items_in_page = sorted_items[
                    item_offset : item_offset + item_count_in_page
                ]

                if next_selected:
                    keyboard = []
                    for item in enumerate(items_in_page):
                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    get_caption_func(item[1]),
                                    callback_data=f"pag-{paginator}-{item[0]}",
                                )
                            ]
                        )
                    next_query = f"pag-{paginator}-next"
                    if show_button == "restart":
                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    RESTART_PAGINATOR_CAPTION, callback_data=next_query
                                )
                            ]
                        )
                    elif show_button == "next":
                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    NEXT_PAGE_CAPTION, callback_data=next_query
                                )
                            ]
                        )

                    if paginator_settings["show_cancel_button"]:
                        keyboard.append(
                            [
                                InlineKeyboardButton(
                                    CANCEL_CAPTION, callback_data="cancel"
                                )
                            ]
                        )

                    self.context_set(f"pag-offset-{paginator}", new_offset)
                    self.context_set(f"pag-inlines-offset-{paginator}", item_offset)
                    self.next(
                        paginator_state,
                        paginator_settings["header"],
                        InlineKeyboardMarkup(keyboard),
                    )

                # if not next_selected:
                else:
                    logger.info(
                        f"Handling selection '{selection}'"
                        f" received for paginator '{paginator}'"
                        f" in conversation {self} with offset {offset}..."
                    )

                    self.context_del(f"pag-offset-{paginator}")
                    self.context_del(f"pag-inlines-offset-{paginator}")

                    # TODO: Don't impose _handler sufix to the framework user
                    selected_item = sorted_items[inlines_offset + selected_index]
                    return getattr(self, paginator_settings["handler"] + "_handler")(
                        selected_item
                    )

        return _paginator_handler_function

    def contact_handler(self, handler):
        def _contact_handler_function(update, context):
            self.update = update
            self.context = context
            contact = self.update.message.contact
            if contact.user_id is None:
                logger.debug("Received a contact without a Telegram ID.")
            else:
                return handler(self.update.message.contact)

        return _contact_handler_function


# TODO: Auto insert cancel inline as command option (but allow manual insert) (II)
# TODO: Consider default state for next state (III)
# add_inline_default_next()?
# TODO: Reserve certain names in inlines: like 'pag-[0-9]+-(([0-9]+)|(next))'
# or 'paginator_proxy'
# TODO: NamedTuples or classes for members with dicts
class StateSet:
    def __init__(self, command):
        self.command = command
        self.texts = {}
        self.inlines = {}
        self.paginators = {}
        self.paginators_inline_proxies = {}
        self.contacts = {}

    def add_text(self, state, handler):
        self.texts[state] = handler

    def add_inline(self, state, handler, caption):
        if state not in self.inlines:
            self.inlines[state] = {}
        self.inlines[state][handler] = caption

    # TODO: Maybe just add_cancel()
    def add_cancel_inline(self, state, cancel_caption=CANCEL_CAPTION):
        self.add_inline(state, "cancel", cancel_caption)

    def add_paginator(
        self,
        state,
        paginator_state,
        inline_caption,
        iterable,
        header,
        empty_message,
        get_caption_func,
        handler,
        page_size=5,
        show_cancel_button=False,
    ):
        if paginator_state not in self.paginators:
            self.paginators[paginator_state] = {}
        # TODO: Refactor this hack
        self.add_paginator_inline_proxy(state, paginator_state, inline_caption)
        self.paginators[paginator_state]["iterable"] = iterable
        self.paginators[paginator_state]["header"] = header
        self.paginators[paginator_state]["empty_message"] = empty_message
        self.paginators[paginator_state]["get_caption_func"] = get_caption_func
        self.paginators[paginator_state]["handler"] = handler
        self.paginators[paginator_state]["page_size"] = page_size
        self.paginators[paginator_state]["show_cancel_button"] = show_cancel_button

    def add_paginator_inline_proxy(self, state, paginator_state, caption):
        if state not in self.paginators_inline_proxies:
            self.paginators_inline_proxies[state] = {}
        self.paginators_inline_proxies[state][paginator_state] = caption

    def paginator_settings(self, paginator):
        return self.paginators[paginator]

    def add_contact(self, state, handler):
        self.contacts[state] = handler

    # TODO: Don't impose _handler sufix to the framework user
    @property
    def graph(self):
        states = {}

        for _id in self.texts:
            if _id not in states:
                states[_id] = []
            states[_id].append(
                MessageHandler(
                    Filters.text,
                    store_update_context_text_command(
                        getattr(self.command, self.texts[_id] + "_handler"),
                        self.command,
                        self.texts[_id],
                    ),
                )
            )

        for _id in self.inlines:
            if _id not in states:
                states[_id] = []
            for inline in self.inlines[_id]:
                states[_id].append(
                    CallbackQueryHandler(
                        self.command.inline_handler(
                            getattr(self.command, inline + "_handler")
                        ),
                        pattern=fr"^{inline}$",
                    )
                )

        for _id in self.paginators:
            if _id not in states:
                states[_id] = []
            states[_id].append(
                CallbackQueryHandler(
                    self.command.paginator_handler(),
                    pattern=(
                        fr"^pag-{_id}-("
                        + "|".join(
                            ["next"]
                            + [
                                str(index)
                                for index in range(
                                    int(self.paginators[_id]["page_size"])
                                )
                            ]
                        )
                        + r")$"
                    ),
                )
            )

        for _id in self.paginators_inline_proxies:
            if _id not in states:
                states[_id] = []
            for inline_proxy in self.paginators_inline_proxies[_id]:
                states[_id].append(
                    CallbackQueryHandler(
                        self.command.paginator_handler(),
                        pattern=(
                            fr"^pag-{inline_proxy}-("
                            + "|".join(
                                ["next"]
                                + [
                                    str(index)
                                    for index in range(
                                        int(self.paginators[inline_proxy]["page_size"])
                                    )
                                ]
                            )
                            + r")$"
                        ),
                    )
                )

        for _id in self.contacts:
            if _id not in states:
                states[_id] = []
            states[_id].append(
                MessageHandler(
                    Filters.contact,
                    self.command.contact_handler(
                        getattr(self.command, self.contacts[_id] + "_handler")
                    ),
                )
            )

        return states


class MarkupBuilder:
    # TODO: Command users depend on this to create 'next' markups (I)
    @property
    def cancel_inline(self):
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(CANCEL_CAPTION, callback_data="cancel")]]
        )

    def from_start(self, all_inlines, all_inline_proxies):
        inlines = all_inlines[ConversationHandlerMixin.START]
        inline_proxies = (
            all_inline_proxies[ConversationHandlerMixin.START]
            if ConversationHandlerMixin.START in all_inline_proxies
            else []
        )
        markup = [
            list(
                InlineKeyboardButton(inlines[handler], callback_data=handler)
                for handler in inlines
                if handler != "cancel"
            )
            + list(
                InlineKeyboardButton(
                    inline_proxies[paginator], callback_data=f"pag-{paginator}-next"
                )
                for paginator in inline_proxies
            )
        ]
        if "cancel" in inlines:
            markup.append(
                [InlineKeyboardButton(inlines["cancel"], callback_data="cancel")]
            )
        return InlineKeyboardMarkup(markup)
