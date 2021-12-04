from fjfnaranjobot.command import BotCommand, CommandHandlerMixin


class Friends(CommandHandlerMixin, BotCommand):
    command_name = "nfriends"
    description = "Manage friends."

    def entrypoint(self):
        self.reply("Not implemented.")
