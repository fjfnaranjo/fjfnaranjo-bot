from telegram.ext import DispatcherHandlerStop

from fjfnaranjobot.auth import only_owner
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

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
