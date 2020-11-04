# TODO: Review all tests
# TODO: Generalize conversation end
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.common import inline_handler, quote_value_for_log
from fjfnaranjobot.components.terraria.models import TerrariaProfile
from fjfnaranjobot.components.terraria.tasks import (
    server_status_chain,
    start_server_chain,
    stop_server_chain,
)
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

KEYBOARD_ROWS = 5

#
# terraria_admin_handler states
#
# cmd --> NEW_OR_CONFIG --> NEW_NAME --> end
#                       --> CONFIG_SELECT --> SELECT_ACTION
#
# SELECT_ACTION --> CONFIG_EDIT
#               --> CONFIG_RENAME --> end
#               --> CONFIG_DELETE --> end
#               --> end (toggle)
#               --> end (status)
#               --> end (start)
#               --> end (stop)
#               --> CONFIG_SERVER
#               --> ADD_USER_CONTACT --> end
#               --> DEL_USER_CONTACT --> end
#               --> DEREGISTER_CHAT --> end
#
# CONFIG_EDIT   -->   CONFIG_EDIT_AWS_DEFAULT_REGION
#                                   V
#                    CONFIG_EDIT_AWS_ACCESS_KEY_ID
#                                   V
#                   CONFIG_EDIT_AWS_SECRET_ACCESS_KEY
#                                   V
#                      CONFIG_EDIT_MICROAPI_TOKEN
#                                   V
#                  CONFIG_EDIT_TSHOCK_REST_API_TOKEN
#                                   V
#                       CONFIG_EDIT_DOMAIN_NAME
#                                   V
#                                  end
#
# CONFIG_SERVER --> START_CONFIRM --> end
#               --> STOP_CONFIRM --> end
#               --> HOLD_CONFIRM --> end
#               --> end (status)
#               --> end (usage)
#
# ADD_USER_CONTACT --> end
#
# DEL_USER_CONTACT --> end
#
# DEREGISTER_CHAT --> DEREGISTER_CHAT
#                 --> end
#
# * --> end
#

(
    NEW_OR_CONFIG,
    NEW_NAME,
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
) = range(12)


def _clear_context_data(context):
    known_keys = [
        "chat_id",
        "message_id",
        "selected_profile",
        "aws_default_region",
        "aws_access_key_id",
        "aws_secret_access_key",
        "microapi_token",
        "tshock_token",
        "dns_name",
        "keyboard_users",
    ]
    for key in known_keys:
        if key in context.user_data:
            del context.user_data[key]


_cancel_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Cancel", callback_data="cancel")]]
)


@only_owner
def terraria_admin_handler(update, context):
    logger.info("Entering 'terraria_admin' conversation.")

    keyboard = [
        [
            InlineKeyboardButton("New", callback_data="new"),
            InlineKeyboardButton("Configure", callback_data="config"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reply = update.message.reply_text(
        "You can create a new Terraria profile or configure an existing one. "
        "You can also cancel the terraria_admin command at any time.",
        reply_markup=reply_markup,
    )
    context.chat_data["chat_id"] = reply.chat.id
    context.chat_data["message_id"] = reply.message_id
    return NEW_OR_CONFIG


def new_handler(_update, context):
    logger.info("Requesting new profile name.")

    context.bot.edit_message_text(
        "Tell me the name for the new profile.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return NEW_NAME


def new_name_handler(update, context):
    # TODO: Validation
    name = update.message.text
    shown_name = quote_value_for_log(name)
    logger.info(f"Received name {shown_name}.")

    new_profile = TerrariaProfile()
    new_profile.name = name
    new_profile.commit()

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    context.bot.send_message(context.chat_data["chat_id"], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


# TODO: Generalize paginator
def config_select_handler(_update, context):
    profiles = [profile for profile in TerrariaProfile.all()]
    if len(profiles) == 0:
        logger.info("Not showing any profile because there are no profiles.")

        context.bot.delete_message(
            context.chat_data["chat_id"],
            context.chat_data["message_id"],
        )
        context.bot.send_message(
            context.chat_data["chat_id"],
            "You don't have any profiles yet.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    else:
        offset = context.chat_data.get("offset", 0)
        logger.info(f"Showing profiles and requesting selection. Offset: {offset}.")

        show_button = None
        keyboard = []
        keyboard_profiles = []
        if len(profiles) <= KEYBOARD_ROWS:
            page_profiles = profiles
        else:
            pending_profiles = profiles[offset:]
            if len(pending_profiles) < KEYBOARD_ROWS:
                show_button = "restart"
                offset = 0
                page_profiles = pending_profiles
            else:
                show_button = "next"
                offset += KEYBOARD_ROWS
                page_profiles = pending_profiles[:KEYBOARD_ROWS]

        for profile in enumerate(page_profiles):
            keyboard.append(
                [InlineKeyboardButton(profile[1].name, callback_data=f"{profile[0]}")]
            )
            keyboard_profiles.append((profile[1].id, profile[1].name))

        if show_button == "restart":
            keyboard.append([InlineKeyboardButton("Start again", callback_data="next")])
        elif show_button == "next":
            keyboard.append([InlineKeyboardButton("Next page", callback_data="next")])

        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        profiles_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data["offset"] = offset
        context.chat_data["keyboard_profiles"] = keyboard_profiles

        context.bot.edit_message_text(
            "Pick a profile from the next list or request the next page (if apply)",
            context.chat_data["chat_id"],
            context.chat_data["message_id"],
            reply_markup=profiles_markup,
        )
        return CONFIG_SELECT


def config_select_name_handler(update, context):
    query = update.callback_query.data
    profile = TerrariaProfile(context.chat_data["keyboard_profiles"][int(query)][0])
    logger.info(
        f"Received selected profile '{profile.name}'. "
        "Asking what to do with selected profile."
    )

    del context.chat_data["keyboard_profiles"]
    context.user_data["selected_profile"] = profile.id

    new_status = "Disable" if profile.status else "Enable"
    keyboard = [
        [
            InlineKeyboardButton("Edit", callback_data="edit"),
        ],
        [
            InlineKeyboardButton("Rename", callback_data="rename"),
        ],
        [
            InlineKeyboardButton("Delete", callback_data="delete"),
        ],
        [
            InlineKeyboardButton(new_status, callback_data="toggle"),
        ],
        [
            InlineKeyboardButton("Status", callback_data="status"),
        ],
        [
            InlineKeyboardButton("Start", callback_data="start"),
        ],
        [
            InlineKeyboardButton("Stop", callback_data="stop"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(
        f"What do you want to do about profile '{profile.name}'.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=reply_markup,
    )
    return SELECT_ACTION


def config_edit_handler(_update, context):
    logger.info("Editing profile. Requesting AWS_DEFAULT_REGION.")

    context.bot.edit_message_text(
        "Tell me the value for AWS_DEFAULT_REGION.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_AWS_DEFAULT_REGION


def config_edit_aws_default_region_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Requesting AWS_ACCESS_KEY_ID.")

    value = update.message.text
    context.user_data["aws_default_region"] = value

    context.bot.edit_message_text(
        "Tell me the value for AWS_ACCESS_KEY_ID.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_AWS_ACCESS_KEY_ID


def config_edit_aws_access_key_id_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Requesting AWS_SECRET_ACCESS_KEY.")

    value = update.message.text
    context.user_data["aws_access_key_id"] = value

    context.bot.edit_message_text(
        "Tell me the value for AWS_SECRET_ACCESS_KEY.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_AWS_SECRET_ACCESS_KEY


def config_edit_aws_secret_access_key_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Requesting microapi token.")

    value = update.message.text
    context.user_data["aws_secret_access_key"] = value

    context.bot.edit_message_text(
        "Tell me the value for microapi token.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_MICROAPI_TOKEN


def config_edit_microapi_token_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Requesting tShock REST API token.")

    value = update.message.text
    context.user_data["microapi_token"] = value

    context.bot.edit_message_text(
        "Tell me the value for tShock REST API token.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_TSHOCK_REST_API_TOKEN


def config_edit_tshock_rest_api_token_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Requesting domain name.")

    value = update.message.text
    context.user_data["tshock_token"] = value

    context.bot.edit_message_text(
        "Tell me the value for domain name.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_EDIT_DOMAIN_NAME


def config_edit_domain_name_handler(update, context):
    # TODO: Validation
    logger.info("Received value. Saving changes.")

    value = update.message.text
    profile = TerrariaProfile(context.user_data["selected_profile"])
    profile.aws_default_region = context.user_data["aws_default_region"]
    profile.aws_access_key_id = context.user_data["aws_access_key_id"]
    profile.aws_secret_access_key = context.user_data["aws_secret_access_key"]
    profile.microapi_token = context.user_data["microapi_token"]
    profile.tshock_token = context.user_data["tshock_token"]
    profile.dns_name = value
    profile.commit()

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(context.chat_data["chat_id"], "Ok.")
    return ConversationHandler.END


def config_edit_rename_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(f"Requesting new name for profile '{profile.name}'.")

    context.bot.edit_message_text(
        "Tell me the new name.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=_cancel_markup,
    )
    return CONFIG_RENAME


def config_edit_rename_name_handler(update, context):
    # TODO: Validation
    new_name = update.message.text
    logger.info(f"Received new name '{new_name}'. Saving changes.")

    profile = TerrariaProfile(context.user_data["selected_profile"])
    old_name = profile.name
    profile.name = new_name
    profile.commit()

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(
        context.chat_data["chat_id"], f"Renamed profile '{old_name}' to '{new_name}'."
    )
    return ConversationHandler.END


def config_edit_delete_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(
        f"Received deletion request for profile {profile.name}. Asking to confirm."
    )

    confirm_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Confirm", callback_data="confirm")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")],
        ]
    )
    context.bot.edit_message_text(
        f"Are you sure that you want to delete the profile '{profile.name}'.",
        context.chat_data["chat_id"],
        context.chat_data["message_id"],
        reply_markup=confirm_markup,
    )
    return CONFIG_DELETE


def config_edit_delete_confirm_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(f"Deleted profile {profile.name}.")

    profile.delete()

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(
        context.chat_data["chat_id"], f"The profile '{profile.name}' was deleted."
    )
    return ConversationHandler.END


def config_edit_toggle_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(
        f"Requested status toggle for profile '{profile.name}'. Saving changes."
    )

    profile.status = not profile.status
    new_status = "enabled" if profile.status else "disabled"
    profile.commit()

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(
        context.chat_data["chat_id"], f"Profile '{profile.name}' {new_status}."
    )
    return ConversationHandler.END


def config_edit_status_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(
        f"Requested server status for profile '{profile.name}'. Calling async task."
    )

    server_status_chain(profile.id, context.chat_data["chat_id"])

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(context.chat_data["chat_id"], "Let me get back to you.")
    return ConversationHandler.END


def config_edit_start_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(
        f"Requested server start for profile '{profile.name}'. Calling async task."
    )

    start_server_chain(profile.id, context.chat_data["chat_id"])

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(context.chat_data["chat_id"], "Let me get back to you.")
    return ConversationHandler.END


def config_edit_stop_handler(_update, context):
    profile = TerrariaProfile(context.user_data["selected_profile"])
    logger.info(
        f"Requested server stop for profile '{profile.name}'. Calling async task."
    )

    stop_server_chain(profile.id, context.chat_data["chat_id"])

    context.bot.delete_message(
        context.chat_data["chat_id"], context.chat_data["message_id"]
    )
    _clear_context_data(context)
    context.bot.send_message(context.chat_data["chat_id"], "Let me get back to you.")
    return ConversationHandler.END


def cancel_handler(_update, context):
    logger.info("Aborting 'terraria_admin' conversation.")

    if "message_id" in context.chat_data:
        context.bot.delete_message(
            context.chat_data["chat_id"], context.chat_data["message_id"]
        )
    context.bot.send_message(context.chat_data["chat_id"], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


cancel_inlines = {
    "cancel": cancel_handler,
}
action_inlines = {
    "new": new_handler,
    "config": config_select_handler,
    "cancel": cancel_handler,
}
list_pos_next_inlines = {
    "0": config_select_name_handler,
    "1": config_select_name_handler,
    "2": config_select_name_handler,
    "3": config_select_name_handler,
    "4": config_select_name_handler,
    "next": config_select_handler,
    "cancel": cancel_handler,
}
config_action_inlines = {
    "edit": config_edit_handler,
    "rename": config_edit_rename_handler,
    "delete": config_edit_delete_handler,
    "toggle": config_edit_toggle_handler,
    "status": config_edit_status_handler,
    "start": config_edit_start_handler,
    "stop": config_edit_stop_handler,
    "cancel": cancel_handler,
}
config_del_confirm_inlines = {
    "confirm": config_edit_delete_confirm_handler,
    "cancel": cancel_handler,
}

terraria_admin_conversation = ConversationHandler(
    entry_points=[CommandHandler("terraria_admin", terraria_admin_handler)],
    states={
        NEW_OR_CONFIG: [
            CallbackQueryHandler(inline_handler(action_inlines, logger)),
        ],
        NEW_NAME: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, new_name_handler),
        ],
        CONFIG_SELECT: [
            CallbackQueryHandler(inline_handler(list_pos_next_inlines, logger)),
        ],
        SELECT_ACTION: [
            CallbackQueryHandler(inline_handler(config_action_inlines, logger)),
        ],
        CONFIG_EDIT_AWS_DEFAULT_REGION: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_aws_default_region_handler),
        ],
        CONFIG_EDIT_AWS_ACCESS_KEY_ID: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_aws_access_key_id_handler),
        ],
        CONFIG_EDIT_AWS_SECRET_ACCESS_KEY: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_aws_secret_access_key_handler),
        ],
        CONFIG_EDIT_MICROAPI_TOKEN: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_microapi_token_handler),
        ],
        CONFIG_EDIT_TSHOCK_REST_API_TOKEN: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_tshock_rest_api_token_handler),
        ],
        CONFIG_EDIT_DOMAIN_NAME: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_domain_name_handler),
        ],
        CONFIG_RENAME: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, config_edit_rename_name_handler),
        ],
        CONFIG_DELETE: [
            CallbackQueryHandler(inline_handler(config_del_confirm_inlines, logger)),
        ],
    },
    fallbacks=[],
)
