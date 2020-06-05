from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from fjfnaranjobot.auth import only_owner
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
    EDIT_PROFILE,
    EDIT_PROFILE_AWS_DEFAULT_REGION,
    EDIT_PROFILE_AWS_ACCESS_KEY_ID,
    EDIT_PROFILE_AWS_SECRET_ACCESS_KEY,
    EDIT_PROFILE_MICROAPI_TOKEN,
    EDIT_PROFILE_TSHOCK_REST_API_TOKEN,
    EDIT_PROFILE_DOMAIN_NAME,
    EDIT_PROFILE_STATUS,
) = range(12)


@only_owner
def terraria_admin_handler(_update, _context):
    pass


def terraria_admin_create_handler(_update, _context):
    pass


def terraria_admin_select_handler(_update, _context):
    pass


def terraria_admin_create_name_handler(_update, _context):
    pass


def terraria_admin_select_profile_handler(_update, _context):
    pass


def terraria_admin_select_action_handler(_update, _context):
    pass


def terraria_admin_edit_profile_handler(_update, _context):
    pass


def terraria_admin_edit_profile_aws_default_region_handler(_update, _context):
    pass


def terraria_admin_edit_profile_aws_access_key_id_handler(_update, _context):
    pass


def terraria_admin_edit_profile_aws_secret_access_key_handler(_update, _context):
    pass


def terraria_admin_edit_profile_microapi_token_handler(_update, _context):
    pass


def terraria_admin_edit_profile_tshock_rest_api_token_handler(_update, _context):
    pass


def terraria_admin_edit_profile_domain_name_handler(_update, _context):
    pass


def terraria_admin_edit_profile_status_handler(_update, _context):
    pass


def terraria_admin_cancel_handler(_update, _context):
    pass


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
        ],
        EDIT_PROFILE: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_AWS_DEFAULT_REGION: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_AWS_ACCESS_KEY_ID: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_AWS_SECRET_ACCESS_KEY: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_MICROAPI_TOKEN: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_TSHOCK_REST_API_TOKEN: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_DOMAIN_NAME: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
        EDIT_PROFILE_STATUS: [
            CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler),
        ],
    },
    fallbacks=[CommandHandler('terraria_admin_cancel', terraria_admin_cancel_handler)],
)
