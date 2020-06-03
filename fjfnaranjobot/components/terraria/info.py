from telegram.ext import CommandHandler, DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner, only_real
from fjfnaranjobot.common import Command
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# terraria_handler states
#
# transition key: -o-> only owner
#                 -p-> only users in profile
#                 -f-> only friends
#
# cmd ---> SELECT_ACTION -o-> CHAT_REGISTER_CHAT_PROFILE ---> end
#                        -f-> REQUEST_SINGUP ---> end
#                        -r-> SHOW_STATUS ---> end
#                        -r-> BROADCAST_STATUS ---> end
#                        -r-> SHOW_USAGE_REPORT ---> end
#                        -r-> BROADCAST_USAGE_REPORT ---> end
#                        -r-> CHAT_START ---> CHAT_START_CONFIRM ---> end
#                        -r-> CHAT_STOP ---> CHAT_STOP_CONFIRM ---> end
#                        -r-> CHAT_HOLD ---> CHAT_HOLD_CONFIRM --> end
#


@only_real
def terraria_handler(_update, _context):
    logger.info("The terraria command is not implemented.")
    raise DispatcherHandlerStop()


#
# terraria_admin_handler states
#
# cmd --> CREATE_OR_SELECT --> CREATE_PROFILE_NAME --> end
#                          --> SELECT_PROFILE --> SELECT_PROFILE
#                                             --> SELECT_ACTION
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


@only_owner
def terraria_admin_handler(_update, _context):
    logger.info("The terraria admin command is not implemented.")
    raise DispatcherHandlerStop()


handlers = (
    CommandHandler('terraria', terraria_handler),
    CommandHandler('terraria_admin', terraria_admin_handler),
)

commands = (
    Command("Manage Terraria servers.", 'terraria', 'terraria'),
    Command("Manage Terraria servers (admin).", None, 'terraria_admin'),
)
