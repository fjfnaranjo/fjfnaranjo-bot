# TODO: Tests
from fjfnaranjobot.backends import config
from fjfnaranjobot.command import BotCommand, ConversationHandlerMixin
from fjfnaranjobot.common import quote_value_for_log
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)


class Config(ConversationHandlerMixin, BotCommand):
    permissions = BotCommand.PermissionsEnum.ONLY_OWNER
    command_name = "nconfig"
    description = "Edit bot configuration."

    GET_VAR, SET_VAR, SET_VALUE, DEL_VAR = range(1, 5)

    def build_states(self, builder):
        """
        START --> GET_VAR --> end(show)
              --> SET_VAR --> SET_VALUE --> end(set)
              --> DEL_VAR --> end(delete)
        """
        with builder(self.START) as state:
            state.message = (
                "You can get the value for a configuration key, "
                "set it of change it if exists, or clear the key. "
                "You can also cancel the config command at any time."
            )
            state.add_jump("Get", self.GET_VAR)
            state.add_jump("Set", self.SET_VAR)
            state.add_jump("Del", self.DEL_VAR)

        with builder(self.GET_VAR) as state:
            state.message = "Tell me what key do you want to get."
            state.text_handler = "get_var"

        with builder(self.SET_VAR) as state:
            state.message = "Tell me what key do you want to set."
            state.text_handler = "set_var"

        with builder(self.SET_VALUE) as state:
            state.text_handler = "set_value"

        with builder(self.DEL_VAR) as state:
            state.message = "Tell me what key do you want to clear."
            state.text_handler = "del_var"

    async def get_var_handler(self, key):
        log_key = quote_value_for_log(key)
        logger.debug(f"Received key name {log_key}.")
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
            log_result = quote_value_for_log(result)
            logger.debug(f"Replying with result {log_result}.")
            await self.end(f"The value for key '{key}' is '{result}'.")

    async def set_var_handler(self, key):
        log_key = quote_value_for_log(key)
        logger.debug(f"Received key name {log_key}.")
        try:
            config[key]
        except ValueError:
            logger.debug("Can't set invalid config key 'invalid-key'.")
            await self.end(f"The key '{key}' is not a valid key.")
        except KeyError:
            pass
        self.chat_data["config_del_key"] = key
        logger.debug("Requesting value to set the key.")
        await self.next(
            self.SET_VALUE,
            f"Tell me what value do you want to put in the key '{key}'.",
        )

    async def set_value_handler(self, value):
        log_value = quote_value_for_log(value)
        logger.debug(f"Received value {log_value}.")
        key = self.chat_data["config_del_key"]
        log_key = quote_value_for_log(key)
        config[key] = value
        logger.debug(f"Stored {log_value} in key {log_key}.")
        await self.end("I'll remember that.")

    async def del_var_handler(self, key):
        log_key = quote_value_for_log(key)
        logger.debug(f"Received key name {log_key}.")
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
            logger.debug(f"Deleting config with key {log_key}.")
            await self.end("I'll forget that.")
