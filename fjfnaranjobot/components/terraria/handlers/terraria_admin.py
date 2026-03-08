# TODO: Tests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from fjfnaranjobot.command import BotCommand, ConversationHandlerMixin
from fjfnaranjobot.common import quote_value_for_log
from fjfnaranjobot.components.terraria.models import TerrariaProfile
from fjfnaranjobot.components.terraria.tasks import (
    server_status_chain,
    start_server_chain,
    stop_server_chain,
)
from fjfnaranjobot.db import IterableDbRelation
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class TerrariaAdmin(ConversationHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "terraria_admin"
    description = "Administer Terraria servers."

    (
        NEW_CONFIG,
        CONFIG_SELECT,
        SELECT_ACTION,
        CONFIG_EDIT_AWS_DEFAULT_REGION,
        CONFIG_EDIT_AWS_ACCESS_KEY_ID,
        CONFIG_EDIT_AWS_SECRET_ACCESS_KEY,
        CONFIG_EDIT_MICROAPI_TOKEN,
        CONFIG_EDIT_TSHOCK_REST_API_TOKEN,
        CONFIG_EDIT_DOMAIN_NAME,
        CONFIG_RENAME,
        CONFIG_DELETE,
    ) = range(1, 12)

    def build_states(self, builder):
        """
        START --> NEW_CONFIG --> end(new_config_name)
                  CONFIG_SELECT* --> SELECT_ACTION

        SELECT_ACTION --> CONFIG_EDIT
                      --> CONFIG_RENAME --> end
                      --> CONFIG_DELETE --> end
                      --> end (toggle)
                      --> end (status)
                      --> end (start)
                      --> end (stop)
                      --> CONFIG_SERVER
                      --> ADD_USER_CONTACT --> end
                      --> DEL_USER_CONTACT --> end
                      --> DEREGISTER_CHAT --> end

        CONFIG_EDIT   -->   CONFIG_EDIT_AWS_DEFAULT_REGION
                                          V
                           CONFIG_EDIT_AWS_ACCESS_KEY_ID
                                          V
                          CONFIG_EDIT_AWS_SECRET_ACCESS_KEY
                                          V
                             CONFIG_EDIT_MICROAPI_TOKEN
                                          V
                         CONFIG_EDIT_TSHOCK_REST_API_TOKEN
                                          V
                              CONFIG_EDIT_DOMAIN_NAME
                                          V
                                         end

        CONFIG_SERVER --> START_CONFIRM --> end
                      --> STOP_CONFIRM --> end
                      --> HOLD_CONFIRM --> end
                      --> end (status)
                      --> end (usage)

        """

        with builder(self.START) as state:
            state.message = (
                "You can create a new Terraria profile or configure an existing one. "
                "You can also cancel the terraria_admin command at any time."
            )
            state.add_jump("New", self.NEW_CONFIG)
            state.add_jump("Config", self.CONFIG_SELECT)

        with builder(self.NEW_CONFIG) as state:
            state.message = "Tell me the name for the new profile."
            state.text_handler = "new_config_name"

        with builder(self.CONFIG_SELECT) as state:
            state.message = (
                "Pick a profile from the next list or request the "
                "next page (if apply)"
            )
            state.add_paginator(
                IterableDbRelation(TerrariaProfile),
                lambda item: item.id,
                lambda item: item.name,
                "You don't have any profiles yet.",
                "config_select",
            )

        with builder(self.SELECT_ACTION) as state:
            state.add_jump("Edit", self.CONFIG_EDIT_AWS_DEFAULT_REGION)
            state.add_jump("Rename", self.CONFIG_RENAME)
            state.add_jump("Delete", self.CONFIG_DELETE)
            state.add_inline("Toggle", "config_edit_toggle")
            state.add_inline("Status", "config_edit_status")
            state.add_inline("Start", "config_edit_start")
            state.add_inline("Stop", "config_edit_stop")

        with builder(self.CONFIG_EDIT_AWS_DEFAULT_REGION) as state:
            state.message = "Tell me the value for AWS_DEFAULT_REGION."
            state.text_handler = "config_edit_aws_default_region"

        with builder(self.CONFIG_EDIT_AWS_ACCESS_KEY_ID) as state:
            state.message = "Tell me the value for AWS_ACCESS_KEY_ID."
            state.text_handler = "config_edit_aws_access_key_id"

        with builder(self.CONFIG_EDIT_AWS_SECRET_ACCESS_KEY) as state:
            state.message = "Tell me the value for AWS_SECRET_ACCESS_KEY."
            state.text_handler = "config_edit_aws_secret_access_key"

        with builder(self.CONFIG_EDIT_MICROAPI_TOKEN) as state:
            state.message = "Tell me the value for microapi token."
            state.text_handler = "config_edit_microapi_token"

        with builder(self.CONFIG_EDIT_TSHOCK_REST_API_TOKEN) as state:
            state.message = "Tell me the value for tShock REST API token."
            state.text_handler = "config_edit_tshock_rest_api_token"

        with builder(self.CONFIG_EDIT_DOMAIN_NAME) as state:
            state.message = "Tell me the value for domain name."
            state.text_handler = "config_edit_domain_name"

        with builder(self.CONFIG_RENAME) as state:
            state.message = "Tell me the new name."
            state.text_handler = "config_edit_rename_name"

        with builder(self.CONFIG_DELETE) as state:
            state.message = "Are you sure that you want to delete the profile?"
            state.add_inline("Confirm", "config_edit_delete_confirm")

    async def new_config_name_handler(self, name):
        # TODO: Validation
        shown_name = quote_value_for_log(name)
        logger.info(f"Received name {shown_name}.")

        new_profile = TerrariaProfile()
        new_profile.name = name
        new_profile.commit()

        await self.end("Ok.")

    async def config_select_handler(self, profile):
        logger.info(
            f"Received selected profile '{profile.name}'. "
            "Asking what to do with selected profile."
        )

        self.user_data["selected_profile"] = profile.id

        new_status = "Disable" if profile.status else "Enable"
        keyboard = [
            [
                InlineKeyboardButton(
                    "Edit", callback_data=f"jump-{self.CONFIG_EDIT_AWS_DEFAULT_REGION}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Rename", callback_data=f"jump-{self.CONFIG_RENAME}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Delete", callback_data=f"jump-{self.CONFIG_DELETE}"
                ),
            ],
            [
                InlineKeyboardButton(new_status, callback_data="config_edit_toggle"),
            ],
            [
                InlineKeyboardButton("Status", callback_data="config_edit_status"),
            ],
            [
                InlineKeyboardButton("Start", callback_data="config_edit_start"),
            ],
            [
                InlineKeyboardButton("Stop", callback_data="config_edit_stop"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.next(
            self.SELECT_ACTION,
            f"What do you want to do about profile '{profile.name}'.",
            reply_markup=reply_markup,
        )

    async def config_edit_aws_default_region_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Requesting AWS_ACCESS_KEY_ID.")
        self.user_data["aws_default_region"] = value
        await self.next(CONFIG_EDIT_AWS_ACCESS_KEY_ID)

    async def config_edit_aws_access_key_id_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Requesting AWS_SECRET_ACCESS_KEY.")
        self.user_data["aws_access_key_id"] = value
        await self.next(CONFIG_EDIT_AWS_SECRET_ACCESS_KEY)

    async def config_edit_aws_secret_access_key_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Requesting microapi token.")
        self.user_data["aws_secret_access_key"] = value
        await self.next(CONFIG_EDIT_MICROAPI_TOKEN)

    async def config_edit_microapi_token_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Requesting tShock REST API token.")
        self.user_data["microapi_token"] = value
        await self.next(CONFIG_EDIT_TSHOCK_REST_API_TOKEN)

    async def config_edit_tshock_rest_api_token_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Requesting domain name.")
        self.user_data["tshock_token"] = value
        await self.next(CONFIG_EDIT_DOMAIN_NAME)

    async def config_edit_domain_name_handler(self, value):
        # TODO: Validation
        logger.info("Received value. Saving changes.")

        profile = TerrariaProfile(self.user_data["selected_profile"])
        profile.aws_default_region = self.user_data["aws_default_region"]
        profile.aws_access_key_id = self.user_data["aws_access_key_id"]
        profile.aws_secret_access_key = self.user_data["aws_secret_access_key"]
        profile.microapi_token = self.user_data["microapi_token"]
        profile.tshock_token = self.user_data["tshock_token"]
        profile.dns_name = value
        profile.commit()

        await self.end()

    async def config_edit_rename_name_handler(self, new_name):
        # TODO: Validation
        logger.info(f"Received new name '{new_name}'. Saving changes.")

        profile = TerrariaProfile(self.user_data["selected_profile"])
        old_name = profile.name
        profile.name = new_name
        profile.commit()

        del self.user_data["selected_profile"]
        await self.end(f"Renamed profile '{old_name}' to '{new_name}'.")

    async def config_edit_delete_confirm_handler(self):
        profile = TerrariaProfile(self.user_data["selected_profile"])
        logger.info(f"Deleted profile {profile.name}.")
        profile.delete()
        await self.end(f"The profile '{profile.name}' was deleted.")

    async def config_edit_toggle_handler(self):
        profile = TerrariaProfile(self.user_data["selected_profile"])
        logger.info(
            f"Requested status toggle for profile '{profile.name}'. Saving changes."
        )

        profile.status = not profile.status
        new_status = "enabled" if profile.status else "disabled"
        profile.commit()

        await self.end(f"Profile '{profile.name}' {new_status}.")

    async def config_edit_status_handler(self):
        profile = TerrariaProfile(self.user_data["selected_profile"])
        logger.info(
            f"Requested server status for profile '{profile.name}'. Calling async task."
        )

        server_status_chain(profile.id, self.chat_data["chat_id"])

        await self.end("Let me get back to you.")

    async def config_edit_start_handler(self):
        profile = TerrariaProfile(self.user_data["selected_profile"])
        logger.info(
            f"Requested server start for profile '{profile.name}'. Calling async task."
        )

        start_server_chain(profile.id, self.chat_data["chat_id"])

        await self.end("Let me get back to you.")

    async def config_edit_stop_handler(self):
        profile = TerrariaProfile(self.user_data["selected_profile"])
        logger.info(
            f"Requested server stop for profile '{profile.name}'. Calling async task."
        )

        stop_server_chain(profile.id, self.chat_data["chat_id"])

        await self.end("Let me get back to you.")
