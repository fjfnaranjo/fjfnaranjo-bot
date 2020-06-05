from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.components.terraria.models import TerrariaProfile
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# terraria_admin_handler states
#
# cmd --> CREATE_OR_SELECT --> CREATE_PROFILE_NAME --> end
#                          --> SELECT_PROFILE --> SELECT_ACTION
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
    CREATE_OR_SELECT,
    CREATE_PROFILE_NAME,
    SELECT_PROFILE,
    SELECT_ACTION,
    EDIT_PROFILE_AWS_DEFAULT_REGION,
    EDIT_PROFILE_AWS_ACCESS_KEY_ID,
    EDIT_PROFILE_AWS_SECRET_ACCESS_KEY,
    EDIT_PROFILE_MICROAPI_TOKEN,
    EDIT_PROFILE_TSHOCK_REST_API_TOKEN,
    EDIT_PROFILE_DOMAIN_NAME,
    EDIT_PROFILE_STATUS,
) = range(11)


def _clear_user_data(context):
    known_keys = [
        'message_ids',
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


@only_owner
def terraria_admin_handler(update, context):
    logger.info("Entering terraria_admin conversation.")
    reply = update.message.reply_text(
        "Create a new Terraria profile using /terraria_admin_create ."
        "Configure your existing Terraria profiles using /terraria_admin_select ."
        "If you want to do something else, /terraria_admin_cancel .",
    )
    context.user_data['message_ids'] = (reply.chat.id, reply.message_id)
    return CREATE_OR_SELECT


def terraria_admin_create_handler(_update, context):
    logger.info("Requesting new profile name.")
    context.bot.edit_message_text(
        "Tell me the name for the new profile. "
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return CREATE_PROFILE_NAME


def terraria_admin_create_name_handler(update, context):
    name = update.message.text
    new_profile = TerrariaProfile()
    new_profile.name = name
    new_profile.commit()
    context.bot.delete_message(*context.user_data['message_ids'])
    _clear_user_data(context)
    update.message.reply_text("Ok.")
    return ConversationHandler.END


def terraria_admin_select_handler(_update, context):
    logger.info("Showing profiles and requesting selection.")
    profiles = [profile.name for profile in TerrariaProfile.all()]
    if len(profiles) == 0:
        context.bot.edit_message_text(
            "You don't have any profile. "
            "Create a new Terraria profile using /terraria_admin_create ."
            "If you want to do something else, /terraria_admin_cancel .",
            *context.user_data['message_ids'],
        )
        return CREATE_OR_SELECT
    else:
        profile_list = '\n'.join(profiles)
        context.bot.edit_message_text(
            f"Pick a profile using its name from the next list:\n\n{profile_list}\n\n"
            "If you want to do something else, /terraria_admin_cancel .",
            *context.user_data['message_ids'],
        )
        return SELECT_PROFILE


def terraria_admin_select_profile_handler(update, context):
    logger.info("Asking what to do with selected profile.")
    name = update.message.text
    profile = TerrariaProfile.select_one(name=name)
    context.user_data['selected_profile'] = profile.id
    context.bot.edit_message_text(
        f"What do you want to do about profile '{profile.name}'. "
        "To edit this profile: /terraria_admin_edit ."
        "If you want to do something else, /terraria_admin_cancel .",
        *context.user_data['message_ids'],
    )
    return SELECT_ACTION


def terraria_admin_edit_profile_handler(_update, context):
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
    _clear_user_data(context)
    update.message.reply_text("Ok.")
    return ConversationHandler.END


def terraria_admin_cancel_handler(update, context):
    logger.info("Abort terraria_admin conversation.")
    if 'message_ids' in context.user_data:
        context.bot.delete_message(*context.user_data['message_ids'])
    _clear_user_data(context)
    update.message.reply_text("Ok.")
    return ConversationHandler.END


terraria_admin_conversation = ConversationHandler(
    entry_points=[CommandHandler('terraria_admin', terraria_admin_handler)],
    states={
        CREATE_OR_SELECT: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            CommandHandler('terraria_admin_create', terraria_admin_create_handler),
            CommandHandler('terraria_admin_select', terraria_admin_select_handler),
        ],
        CREATE_PROFILE_NAME: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(Filters.text, terraria_admin_create_name_handler),
        ],
        SELECT_PROFILE: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(Filters.text, terraria_admin_select_profile_handler),
        ],
        SELECT_ACTION: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            CommandHandler('terraria_admin_edit', terraria_admin_edit_profile_handler),
        ],
        EDIT_PROFILE_AWS_DEFAULT_REGION: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_default_region_handler
            ),
        ],
        EDIT_PROFILE_AWS_ACCESS_KEY_ID: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_access_key_id_handler
            ),
        ],
        EDIT_PROFILE_AWS_SECRET_ACCESS_KEY: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_aws_secret_access_key_handler
            ),
        ],
        EDIT_PROFILE_MICROAPI_TOKEN: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_microapi_token_handler
            ),
        ],
        EDIT_PROFILE_TSHOCK_REST_API_TOKEN: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_tshock_rest_api_token_handler
            ),
        ],
        EDIT_PROFILE_DOMAIN_NAME: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(
                Filters.text, terraria_admin_edit_profile_domain_name_handler
            ),
        ],
        EDIT_PROFILE_STATUS: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
            MessageHandler(Filters.text, terraria_admin_edit_profile_status_handler),
        ],
    },
    fallbacks=[CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler)],
)
