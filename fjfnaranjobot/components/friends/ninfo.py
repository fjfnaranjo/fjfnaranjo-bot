from fjfnaranjobot.command import BotCommand, CommandHandlerMixin


class Friends(BotCommand, CommandHandlerMixin):
    command_name = "nfriends"
    description = "Manage friends."

    def handle_command(self):
        self.reply("Not implemented.")
