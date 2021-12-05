from fjfnaranjobot.command import BotCommand, CommandHandlerMixin


class Friends(CommandHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "nfriends"
    description = "Manage friends."

    def entrypoint(self):
        self.reply("Not implemented.")
