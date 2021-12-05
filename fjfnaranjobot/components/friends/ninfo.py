# TODO: Tests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from fjfnaranjobot.auth import friends
from fjfnaranjobot.command import BotCommand, ConversationHandlerMixin
from fjfnaranjobot.common import User, quote_value_for_log
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# Friends conversation states
#
# cmd --> START --> LIST       --> LIST
#                              --> DEL_FRIEND_CONFIRM --> end
#                              --> end
#               --> ADD_FRIEND --> end
#               --> DEL_FRIEND --> end
#


class Friends(ConversationHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "nfriends"
    description = "Manage friends."
    initial_text = (
        "You can list all your friends. "
        "Also, you can add or remove Telegram contacts and IDs to the list. "
        "You can also cancel the friends command at any time."
    )

    chat_data_known_keys = [
        "delete_user",
    ]

    class StatesEnum:
        LIST, DEL_FRIEND_CONFIRM, ADD_FRIEND, DEL_FRIEND = range(1, 5)

    def __init__(self):
        super().__init__()

        # TODO: Consider default state for next state (II)
        # add_inline_default_next()?

        self.states.add_cancel_inline(ConversationHandlerMixin.START)
        self.states.add_paginator(
            ConversationHandlerMixin.START,
            Friends.StatesEnum.LIST,
            "List",
            friends,
            "Your friends will be listed below in pages. "
            "You can request the next page (if apply) or "
            "select a friend if you want to remove it.",
            "You have no friends.",
            lambda item: item.id,
            lambda item: item.username,
            "list_del_confirm",
            show_cancel_button=True,
        )
        self.states.add_inline(ConversationHandlerMixin.START, "add", "Add")
        self.states.add_inline(ConversationHandlerMixin.START, "del", "Delete")

        self.states.add_cancel_inline(Friends.StatesEnum.LIST)

        self.states.add_cancel_inline(Friends.StatesEnum.ADD_FRIEND)
        # self.states.add_contact(Friends.StatesEnum.ADD_FRIEND, "add_friend")
        self.states.add_text(Friends.StatesEnum.ADD_FRIEND, "add_friend_id")

        self.states.add_cancel_inline(Friends.StatesEnum.DEL_FRIEND)
        # self.states.add_contact(Friends.StatesEnum.DEL_FRIEND, "del_friend")
        self.states.add_text(Friends.StatesEnum.DEL_FRIEND, "del_friend_id")

        # TODO: Consider generic 'confirm' state
        self.states.add_cancel_inline(Friends.StatesEnum.DEL_FRIEND_CONFIRM)
        self.states.add_inline(
            Friends.StatesEnum.DEL_FRIEND_CONFIRM, "list_del_confirmed", "Confirm"
        )

    # list_del_confirm_inlines = {
    #     "confirm": Friends.list_del_confirmed_handler,
    # }
    def list_del_confirm_handler(self, item_id, item_caption):
        logger.debug(
            f"Received in-list friend deletion request for friend {item_caption}"
            f" with id {item_id}. Asking to confirm."
        )

        user_to_delete = User(item_id, item_caption)
        self.context.chat_data["delete_user"] = (
            user_to_delete.id,
            user_to_delete.username,
        )

        confirm_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Confirm", callback_data="list_del_confirmed")],
                [InlineKeyboardButton("Cancel", callback_data="cancel")],
            ]
        )

        self.next(
            Friends.StatesEnum.DEL_FRIEND_CONFIRM,
            f"Are you sure that you want to remove '{user_to_delete.username}' as a friend.",
            confirm_markup,
        )

    def list_del_confirmed_handler(self):
        logger.info("Received confirmation for deletion.")

        delete_user = User(*self.context.chat_data["delete_user"])
        del self.context.chat_data["delete_user"]
        friends.discard(delete_user)

        self.end("Ok.")

    def add_handler(self):
        logger.info("Requesting contact to add as a friend.")
        self.next(
            Friends.StatesEnum.ADD_FRIEND,
            "Send me the contact of the friend you want to add. Or its id.",
            self.markup.cancel_inline,
        )

    def add_friend_handler(self):
        contact = self.update.message.contact
        if contact.user_id is None:
            logger.info("Received a contact without a Telegram ID.")
            self.end("That doesn't look like a Telegram user.")

        contact_first_name = getattr(contact, "first_name", "")
        contact_last_name = getattr(contact, "last_name", "")
        first_name = contact_first_name if contact_first_name is not None else ""
        last_name = contact_last_name if contact_last_name is not None else ""
        username = " ".join([first_name, last_name]).strip()
        user = User(contact.user_id, username)

        logger.info(f"Received a contact. Adding {user.username} as a friend.")
        friends.add(user)
        self.end(f"Added {user.username} as a friend.")

    def add_friend_id_handler(self):
        try:
            (user_id,) = self.update.message.text.split()
        except ValueError:

            shown_id = quote_value_for_log(self.update.message.text)
            logger.info(f"Received and invalid id {shown_id} trying to add a friend.")

            self.end("That's not a contact nor a single valid id.")

        else:
            try:
                user_id_int = int(user_id)
                if user_id_int < 0:
                    raise ValueError()
            except ValueError:

                logger.info(
                    f"Received and invalid number in id '{user_id}' trying to add a friend."
                )
                self.end("That's not a contact nor a valid id.")

            else:

                user = User(user_id_int, f"ID {user_id_int}")
                logger.info(f"Adding {user.username} as a friend.")

                friends.add(user)

                self.end(f"Added {user.username} as a friend.")

    def del_handler(self):
        logger.info("Requesting contact to remove as a friend.")
        self.next(
            Friends.StatesEnum.DEL_FRIEND,
            "Send me the contact of the friend you want to remove. Or its id.",
            self.markup.cancel_inline,
        )

    def del_friend_handler(self):
        contact = self.update.message.contact

        if contact.user_id is None:
            logger.info("Received a contact without a Telegram ID.")
            self.end("That doesn't look like a Telegram user.")

        contact_first_name = getattr(contact, "first_name", "")
        contact_last_name = getattr(contact, "last_name", "")
        first_name = contact_first_name if contact_first_name is not None else ""
        last_name = contact_last_name if contact_last_name is not None else ""
        username = " ".join([first_name, last_name]).strip()
        user = User(contact.user_id, username)

        if user in friends:

            for friend in friends:
                if friend.id == user.id:
                    friend_username = friend.username
            logger.info(f"Removing {friend_username} as a friend.")

            friends.discard(user)

            self.end(f"Removed {friend_username} as a friend.")

        else:

            logger.info(f"Not removing {user.username} because its not a friend.")

            self.end(f"{user.username} isn't a friend.")

    def del_friend_id_handler(self):
        try:
            (user_id,) = self.update.message.text.split()
        except ValueError:

            shown_id = quote_value_for_log(self.update.message.text)
            logger.info(
                f"Received and invalid id {shown_id} trying to remove a friend."
            )

            self.end("That's not a contact nor a single valid id.")

        else:
            try:
                user_id_int = int(user_id)
                if user_id_int < 0:
                    raise ValueError()
            except ValueError:

                logger.info(
                    f"Received and invalid number in id '{user_id}' trying to remove a friend."
                )
                self.end("That's not a contact nor a valid id.")

            else:
                user = User(user_id_int, f"ID {user_id_int}")
                if user in friends:

                    for friend in friends:
                        if friend.id == user.id:
                            friend_username = friend.username
                    logger.info(f"Removing {friend_username} as a friend.")

                    friends.discard(user)

                    self.end(f"Removed {friend_username} as a friend.")

                else:
                    logger.info(
                        f"Not removing {user.username} because its not a friend."
                    )

                    self.end(f"{user.username} isn't a friend.")
