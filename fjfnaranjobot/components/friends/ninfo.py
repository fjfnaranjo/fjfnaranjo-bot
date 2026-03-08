# TODO: Tests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from fjfnaranjobot.auth import friends
from fjfnaranjobot.command import BotCommand, ConversationHandlerMixin
from fjfnaranjobot.common import User, quote_value_for_log
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Friends(ConversationHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "nfriends"
    description = "Manage friends."

    LIST, DEL_FRIEND_CONFIRM, ADD_FRIEND, ADD_FRIEND_ID_NAME, DEL_FRIEND = range(1, 6)

    def build_states(self, builder):
        """
        START --> LIST*      --> DEL_FRIEND_CONFIRM --> end(delete)
              --> ADD_FRIEND --> ADD_FRIEND_ID_NAME --> end(add)
              --> DEL_FRIEND --> end(delete)
        """
        with builder(self.START) as state:
            state.message = (
                "You can list all your friends. "
                "Also, you can add or remove Telegram contacts and IDs to the list. "
                "You can also cancel the friends command at any time."
            )
            state.add_jump("List", self.LIST)
            state.add_jump("Add", self.ADD_FRIEND)
            state.add_jump("Delete", self.DEL_FRIEND)

        with builder(self.LIST) as state:
            state.message = (
                "Your friends will be listed below in pages. "
                "You can request the next page (if apply) or "
                "select a friend if you want to remove it."
            )
            state.add_paginator(
                friends,
                lambda item: item.id,
                lambda item: item.username,
                "You have no friends.",
                "list_del_confirm",
            )

        with builder(self.DEL_FRIEND_CONFIRM) as state:
            state.add_inline("Confirm", "list_del_confirmed")

        with builder(self.ADD_FRIEND) as state:
            state.message = (
                "Send me the contact of the friend you want to add. Or its id."
            )
            state.contact_handler = "add_friend"
            state.text_handler = "add_friend_id"

        with builder(self.ADD_FRIEND_ID_NAME) as state:
            state.text_handler = "add_friend_id_name"

        with builder(self.DEL_FRIEND) as state:
            state.message = (
                "Send me the contact of the friend you want to remove. Or its id."
            )
            state.contact_handler = "del_friend"
            state.text_handler = "del_friend_id"

    async def list_del_confirm_handler(self, item):
        item_id = item.id
        item_caption = item.username

        logger.debug(
            f"Received in-list friend deletion request for friend {item_caption}"
            f" with id {item_id}. Asking to confirm."
        )

        user_to_delete = User(item_id, item_caption)
        self.context.chat_data["friends_delete_user"] = (
            user_to_delete.id,
            user_to_delete.username,
        )

        await self.next(
            self.DEL_FRIEND_CONFIRM,
            f"Are you sure that you want to remove '{user_to_delete.username}' as a friend.",
        )

    async def list_del_confirmed_handler(self):
        logger.debug("Received confirmation for deletion.")

        delete_user = User(*self.context.chat_data.pop("friends_delete_user"))
        friends.discard(delete_user)

        await self.end()

    async def add_friend_handler(self, contact):
        contact_first_name = getattr(contact, "first_name", "")
        contact_last_name = getattr(contact, "last_name", "")
        first_name = contact_first_name if contact_first_name is not None else ""
        last_name = contact_last_name if contact_last_name is not None else ""
        username = " ".join([first_name, last_name]).strip()
        user = User(contact.user_id, username)

        logger.debug(f"Received a contact. Adding {user.username} as a friend.")
        friends.add(user)
        await self.end(f"Added {user.username} as a friend.")

    async def add_friend_id_handler(self, text):
        try:
            (user_id,) = text.split()
        except ValueError:
            shown_id = quote_value_for_log(text)
            logger.debug(f"Received and invalid id {shown_id} trying to add a friend.")
            await self.end("That's not a contact nor a single valid id.")

        else:
            try:
                user_id_int = int(user_id)
                if user_id_int < 0:
                    raise ValueError()
            except ValueError:
                logger.debug(
                    f"Received and invalid number in id '{user_id}' trying to add a friend."
                )
                await self.end("That's not a contact nor a valid id.")
            else:
                self.context.chat_data["friends_add_user_id"] = user_id_int
                await self.next(
                    self.ADD_FRIEND_ID_NAME,
                    "Send me a name for the contact.",
                )

    async def add_friend_id_name_handler(self, text):
        logger.debug("Received contact username.")
        try:
            (username,) = text.split()
        except ValueError:
            shown_username = quote_value_for_log(text)
            logger.debug(
                f"Received and invalid username {shown_username} trying to add a friend by id."
            )
            await self.end("That's not a valid contact username.")

        user_id_int = self.context.chat_data.pop("friends_add_user_id")
        user = User(user_id_int, username)
        logger.debug(f"Adding {user.username} as a friend.")
        friends.add(user)
        await self.end(f"Added {user.username} as a friend.")

    async def del_friend_handler(self, contact):
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
            logger.debug(f"Removing {friend_username} as a friend.")

            friends.discard(user)

            await self.end(f"Removed {friend_username} as a friend.")

        else:
            logger.debug(f"Not removing {user.username} because its not a friend.")

            await self.end(f"{user.username} isn't a friend.")

    async def del_friend_id_handler(self, text):
        try:
            (user_id,) = text.split()
        except ValueError:
            shown_id = quote_value_for_log(text)
            logger.debug(
                f"Received and invalid id {shown_id} trying to remove a friend."
            )

            await self.end("That's not a contact nor a single valid id.")

        else:
            try:
                user_id_int = int(user_id)
                if user_id_int < 0:
                    raise ValueError()
            except ValueError:
                logger.debug(
                    f"Received and invalid number in id '{user_id}' trying to remove a friend."
                )
                await self.end("That's not a contact nor a valid id.")

            else:
                user = User(user_id_int, f"ID {user_id_int}")
                if user in friends:
                    for friend in friends:
                        if friend.id == user.id:
                            friend_username = friend.username
                    logger.debug(f"Removing {friend_username} as a friend.")

                    friends.discard(user)

                    await self.end(f"Removed {friend_username} as a friend.")

                else:
                    logger.debug(
                        f"Not removing {user.username} because its not a friend."
                    )

                    await self.end(f"{user.username} isn't a friend.")
