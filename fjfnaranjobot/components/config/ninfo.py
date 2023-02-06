# TODO: Tests
from fjfnaranjobot.backends import config
from fjfnaranjobot.command import BotCommand, ConversationHandlerMixin
from fjfnaranjobot.common import quote_value_for_log
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# Config conversation states
#
# cmd --> START --> GET_VAR --> end
#               --> SET_VAR --> SET_VALUE --> end
#               --> DEL_VAR --> end
#


class Config(ConversationHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "nconfig"
    description = "Edit bot configuration."
    initial_text = (
        "You can get the value for a configuration key, "
        "set it of change it if exists, or clear the key. "
        "You can also cancel the config command at any time."
    )

    class StatesEnum:
        GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(1, 5)

    def __init__(self):
        super().__init__()

        # TODO: Consider default state for next state (I)
        # add_inline_default_next()?

        self.states.add_cancel_inline(ConversationHandlerMixin.START)
        self.states.add_inline(ConversationHandlerMixin.START, "get", "Get")
        self.states.add_inline(ConversationHandlerMixin.START, "set", "Set")
        self.states.add_inline(ConversationHandlerMixin.START, "del", "Del")

        self.states.add_cancel_inline(Config.StatesEnum.GET_VAR)
        self.states.add_text(Config.StatesEnum.GET_VAR, "get_var")

        self.states.add_cancel_inline(Config.StatesEnum.SET_VAR)
        self.states.add_text(Config.StatesEnum.SET_VAR, "set_var")

        self.states.add_cancel_inline(Config.StatesEnum.DEL_VAR)
        self.states.add_text(Config.StatesEnum.DEL_VAR, "del_var")

        self.states.add_cancel_inline(Config.StatesEnum.SET_VALUE)
        self.states.add_text(Config.StatesEnum.SET_VALUE, "set_value")

    async def get_handler(self):
        logger.debug("Requesting key name to get its value.")
        await self.next(
            Config.StatesEnum.GET_VAR,
            "Tell me what key do you want to get.",
            self.markup.cancel_inline,
        )

    async def get_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            result = config[key]
        except (ValueError, KeyError) as e:
            if isinstance(e, ValueError):
                logger.debug("Key was invalid.")
                await self.end(f"The key '{key}' is not a valid key.")
            else:
                logger.debug("Key doesn't exists.")
                await self.end(f"The key '{key}' doesn't exists.")
        else:
            shown_result = quote_value_for_log(result)
            logger.debug(f"Replying with result {shown_result}.")
            await self.end(f"The value for key '{key}' is '{result}'.")

    async def set_handler(self):
        logger.debug("Requesting key name to set its value.")
        await self.next(
            Config.StatesEnum.SET_VAR,
            "Tell me what key do you want to set.",
            reply_markup=self.markup.cancel_inline,
        )

    async def set_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            config[key]
        except ValueError:
            logger.debug("Can't set invalid config key 'invalid-key'.")
            await self.end(f"The key '{key}' is not a valid key.")
        except KeyError:
            pass
        self.context_set("key", key)
        logger.debug("Requesting value to set the key.")
        await self.next(
            Config.StatesEnum.SET_VALUE,
            f"Tell me what value do you want to put in the key '{key}'.",
            reply_markup=self.markup.cancel_inline,
        )

    async def set_value_handler(self):
        value = self.update.message.text
        shown_value = quote_value_for_log(value)
        logger.debug(f"Received value {shown_value}.")
        key = self.context_del("key")
        config[key] = value
        logger.debug(f"Stored {shown_value} in key '{key}'.")
        await self.end("I'll remember that.")

    async def del_handler(self):
        logger.debug("Requesting key name to clear its value.")
        await self.next(
            Config.StatesEnum.DEL_VAR,
            "Tell me what key do you want to clear.",
            reply_markup=self.markup.cancel_inline,
        )

    async def del_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            del config[key]
        except (ValueError, KeyError) as e:
            if isinstance(e, ValueError):
                logger.debug("Key was invalid.")
                await self.end(f"The key '{key}' is not a valid key.")
            else:
                logger.debug("Key doesn't exists.")
                await self.end(f"The key '{key}' doesn't exists.")
        else:
            logger.debug(f"Deleting config with key '{key}'.")
            await self.end("I'll forget that.")
