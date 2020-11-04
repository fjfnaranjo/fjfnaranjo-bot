from telegram.ext.commandhandler import CommandHandler


class Command:
    name = ''

    @property
    def handler(self):
        return CommandHandler(self.name, self.entrypoint)

    def entrypoint(self, update, context):
        pass


class BotCommand(Command):
    description = ''
    is_prod_command = False
    is_dev_command = False

    # TODO: Remove proxy
    @property
    def prod_command(self):
        return self.name
    @property
    def dev_command(self):
        return self.name


class TextCommand(Command):
    pass


class ContactCommand(Command):
    pass
