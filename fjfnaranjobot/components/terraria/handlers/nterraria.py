# TODO: Tests
from fjfnaranjobot.command import BotCommand, CommandHandlerMixin
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


class Terraria(CommandHandlerMixin, BotCommand):
    command_name = "nterraria"
    description = "Manage Terraria servers."
    allow_chats = True

    async def handle(self):
        reply = "The 'terraria' command is not implemented."
        logger.warning(reply)
        await self.reply(reply)
