# TODO: Review all tests
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
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

KEYBOARD_ROWS = 5

#
# terraria_admin_handler states
#
# cmd --> NEW_OR_CONFIG --> NEW_NAME --> end
#                       --> CONFIG_SELECT --> SELECT_ACTION
#
# SELECT_ACTION --> MANAGE_SERVER
#               --> EDIT_PROFILE
#               --> RENAME_PROFILE_NAME
#               --> DELETE_PROFILE_NAME
#               --> ADD_USER_CONTACT
#               --> DEL_USER_CONTACT
#               --> DEREGISTER_CHAT
#
# MANAGE_SERVER --> START --> START_CONFIRM --> end
#               --> STOP --> STOP_CONFIRM --> end
#               --> HOLD --> HOLD_CONFIRM --> end
#               --> STATUS --> end
#               --> USAGE_REPORT --> end
#
# EDIT_PROFILE --> EDIT_PROFILE
#              -->   EDIT_PROFILE_AWS_DEFAULT_REGION
#                                   V
#                    EDIT_PROFILE_AWS_ACCESS_KEY_ID
#                                   V
#                   EDIT_PROFILE_AWS_SECRET_ACCESS_KEY
#                                   V
#                      EDIT_PROFILE_MICROAPI_TOKEN
#                                   V
#                  EDIT_PROFILE_TSHOCK_REST_API_TOKEN
#                                   V
#                       EDIT_PROFILE_DOMAIN_NAME
#                                   V
#                         EDIT_PROFILE_STATUS
#                                   V
#                                  end
#
# RENAME_PROFILE_NAME --> end
#
# DELETE_PROFILE_NAME --> end
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
    EDIT_PROFILE_AWS_DEFAULT_REGION,
    EDIT_PROFILE_AWS_ACCESS_KEY_ID,
    EDIT_PROFILE_AWS_SECRET_ACCESS_KEY,
    EDIT_PROFILE_MICROAPI_TOKEN,
    EDIT_PROFILE_TSHOCK_REST_API_TOKEN,
    EDIT_PROFILE_DOMAIN_NAME,
    EDIT_PROFILE_STATUS,
) = range(11)


def _clear_context_data(context):
    known_keys = [
        'chat_id',
        'message_id',
        'selected_profile',
        'aws_default_region',
        'aws_access_key_id',
        'aws_secret_access_key',
        'microapi_token',
        'tshock_token',
        'dns_name',
        'status',
    ]
    for key in known_keys:
        if key in context.user_data:
            del context.user_data[key]


_cancel_markup = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
)


@only_owner
def terraria_admin_handler(update, context):
    logger.info("Entering terraria_admin conversation.")

    keyboard = [
        [
            InlineKeyboardButton("New", callback_data='new'),
            InlineKeyboardButton("Configure", callback_data='config'),
        ],
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reply = update.message.reply_text(
        "You can create a new Terraria profile or configure an existing one. "
        "You can also cancel the terraria_admin command at any time.",
        reply_markup=reply_markup,
    )
    context.chat_data['chat_id'] = reply.chat.id
    context.chat_data['message_id'] = reply.message_id
    return NEW_OR_CONFIG


def new_handler(_update, context):
    logger.info("Requesting new profile name.")

    context.bot.edit_message_text(
        "Tell me the name for the new profile.",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=_cancel_markup,
    )
    return NEW_NAME


def new_name_handler(update, context):
    name = update.message.text
    shown_name = quote_value_for_log(name)
    logger.info(f"Received name {shown_name}.")

    new_profile = TerrariaProfile()
    new_profile.name = name
    new_profile.commit()

    context.bot.delete_message(
        context.chat_data['chat_id'], context.chat_data['message_id']
    )
    context.bot.send_message(context.chat_data['chat_id'], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


def config_select_handler(_update, context):
    profiles = [profile for profile in TerrariaProfile.all()]
    if len(profiles) == 0:
        logger.info("Not showing any profile because there are no profiles.")

        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id'],
        )
        context.bot.send_message(
            context.chat_data['chat_id'], "You don't have any profile yet.",
        )
        _clear_context_data(context)
        return ConversationHandler.END

    else:
        offset = context.chat_data.get('offset', 0)
        logger.info(f"Showing profiles and requesting selection. Offset: {offset}.")

        show_button = None
        keyboard = []
        keyboard_profiles = []
        if len(profiles) <= KEYBOARD_ROWS:
            page_profiles = profiles
        else:
            pending_profiles = profiles[offset:]
            if len(pending_profiles) < KEYBOARD_ROWS:
                show_button = 'restart'
                offset = 0
                page_profiles = pending_profiles
            else:
                show_button = 'next'
                offset += KEYBOARD_ROWS
                page_profiles = pending_profiles[:KEYBOARD_ROWS]

        for profile in enumerate(page_profiles):
            keyboard.append(
                [InlineKeyboardButton(profile[1].name, callback_data=f'{profile[0]}')]
            )
            keyboard_profiles.append((profile[1].id, profile[1].name))

        if show_button == 'restart':
            keyboard.append([InlineKeyboardButton("Start again", callback_data='next')])
        elif show_button == 'next':
            keyboard.append([InlineKeyboardButton("Next page", callback_data='next')])

        keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
        profiles_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data['offset'] = offset
        context.chat_data['keyboard_profiles'] = keyboard_profiles

        context.bot.edit_message_text(
            "Pick a profile from the next list or request the next page (if apply)",
            context.chat_data['chat_id'],
            context.chat_data['message_id'],
            reply_markup=profiles_markup,
        )
        return CONFIG_SELECT


def config_select_name_handler(update, context):
    query = update.callback_query.data
    logger.info(
        f"Received selected position {query}. "
        "Asking what to do with selected profile."
    )

    profile = TerrariaProfile.select_one(
        id=context.chat_data['keyboard_profiles'][int(query)][0]
    )
    context.user_data['selected_profile'] = profile.id

    keyboard = [
        [InlineKeyboardButton("Edit", callback_data='edit'),],
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.edit_message_text(
        f"What do you want to do about profile '{profile.name}'. ",
        context.chat_data['chat_id'],
        context.chat_data['message_id'],
        reply_markup=reply_markup,
    )
    return SELECT_ACTION


def config_edit_handler(_update, context):
    logger.info("Editing profile: Requesting AWS_DEFAULT_REGION.")

    context.bot.edit_message_text(
        "Tell me the value for AWS_DEFAULT_REGION. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_AWS_DEFAULT_REGION


def terraria_admin_edit_profile_aws_default_region_handler(update, context):
    logger.info("Editing profile: Requesting AWS_ACCESS_KEY_ID.")

    value = update.message.text
    context.user_data['aws_default_region'] = value

    context.bot.edit_message_text(
        "Tell me the value for AWS_ACCESS_KEY_ID. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_AWS_ACCESS_KEY_ID


def terraria_admin_edit_profile_aws_access_key_id_handler(update, context):
    logger.info("Editing profile: Requesting AWS_SECRET_ACCESS_KEY.")

    value = update.message.text
    context.user_data['aws_access_key_id'] = value

    context.bot.edit_message_text(
        "Tell me the value for AWS_SECRET_ACCESS_KEY. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_AWS_SECRET_ACCESS_KEY


def terraria_admin_edit_profile_aws_secret_access_key_handler(update, context):
    logger.info("Editing profile: Requesting microapi token.")

    value = update.message.text
    context.user_data['aws_secret_access_key'] = value

    context.bot.edit_message_text(
        "Tell me the value for microapi token. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_MICROAPI_TOKEN


def terraria_admin_edit_profile_microapi_token_handler(update, context):
    logger.info("Editing profile: Requesting tShock REST API token.")

    value = update.message.text
    context.user_data['microapi_token'] = value

    context.bot.edit_message_text(
        "Tell me the value for tShock REST API token. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_TSHOCK_REST_API_TOKEN


def terraria_admin_edit_profile_tshock_rest_api_token_handler(update, context):
    logger.info("Editing profile: Requesting domain name.")

    value = update.message.text
    context.user_data['tshock_token'] = value

    context.bot.edit_message_text(
        "Tell me the value for domain name. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_DOMAIN_NAME


def terraria_admin_edit_profile_domain_name_handler(update, context):
    logger.info("Editing profile: Requesting status.")

    value = update.message.text
    context.user_data['dns_name'] = value

    context.bot.edit_message_text(
        "Tell me the value for status (0 or 1). "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return EDIT_PROFILE_STATUS


def terraria_admin_edit_profile_status_handler(update, context):
    logger.info("Editing profile: Saving changes.")

    value = update.message.text
    context.user_data['status'] = value
    profile = TerrariaProfile.select_one(id=context.user_data['selected_profile'])
    profile.aws_default_region = context.user_data['aws_default_region']
    profile.aws_access_key_id = context.user_data['aws_access_key_id']
    profile.aws_secret_access_key = context.user_data['aws_secret_access_key']
    profile.microapi_token = context.user_data['microapi_token']
    profile.tshock_token = context.user_data['tshock_token']
    profile.dns_name = context.user_data['dns_name']
    profile.status = bool(context.user_data['status'])
    profile.commit()

    context.bot.delete_message(*context.user_data['message_ids'])
    _clear_context_data(context)
    update.message.reply_text("Ok.")
    return ConversationHandler.END


def cancel_handler(update, context):
    logger.info("Abort terraria_admin conversation.")

    if 'message_id' in context.chat_data:
        context.bot.delete_message(
            context.chat_data['chat_id'], context.chat_data['message_id']
        )
    context.bot.send_message(context.chat_data['chat_id'], "Ok.")
    _clear_context_data(context)
    return ConversationHandler.END


cancel_inlines = {
    'cancel': cancel_handler,
}
action_inlines = {
    'new': new_handler,
    'config': config_select_handler,
    'cancel': cancel_handler,
}
list_pos_next_inlines = {
    '0': config_select_name_handler,
    '1': config_select_name_handler,
    '2': config_select_name_handler,
    '3': config_select_name_handler,
    '4': config_select_name_handler,
    'next': config_select_handler,
    'cancel': cancel_handler,
}
config_action_inlines = {
    'edit': config_edit_handler,
    'cancel': cancel_handler,
}

terraria_admin_conversation = ConversationHandler(
    entry_points=[CommandHandler('terraria_admin', terraria_admin_handler)],
    states={
        NEW_OR_CONFIG: [CallbackQueryHandler(inline_handler(action_inlines, logger)),],
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
        EDIT_PROFILE_AWS_DEFAULT_REGION: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_default_region_handler
            ),
        ],
        EDIT_PROFILE_AWS_ACCESS_KEY_ID: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_access_key_id_handler
            ),
        ],
        EDIT_PROFILE_AWS_SECRET_ACCESS_KEY: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_secret_access_key_handler
            ),
        ],
        EDIT_PROFILE_MICROAPI_TOKEN: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_microapi_token_handler
            ),
        ],
        EDIT_PROFILE_TSHOCK_REST_API_TOKEN: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_tshock_rest_api_token_handler
            ),
        ],
        EDIT_PROFILE_DOMAIN_NAME: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_domain_name_handler
            ),
        ],
        EDIT_PROFILE_STATUS: [
            CallbackQueryHandler(inline_handler(cancel_inlines, logger)),
            MessageHandler(Filters.text, terraria_admin_edit_profile_status_handler),
        ],
    },
    fallbacks=[],
)
