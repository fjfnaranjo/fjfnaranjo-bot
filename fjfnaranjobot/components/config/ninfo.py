# TODO: Review all tests
from fjfnaranjobot.command import (
    BotCommand,
    ConversationHandlerMixin,
    MarkupBuilder,
    StateSet,
    store_update_context,
)
from fjfnaranjobot.common import quote_value_for_log
from fjfnaranjobot.config import config
from fjfnaranjobot.logging import getLogger

logger = getLogger(__name__)

#
# config_handler states
#
# cmd --> START --> GET_VAR --> end
#               --> SET_VAR --> SET_VALUE --> end
#               --> DEL_VAR --> end
#
# * --> end
#


class Config(BotCommand, ConversationHandlerMixin):
    command_name = "nconfig"
    description = "Edit bot configuration."
    initial_text = (
        "You can get the value for a configuration key, "
        "set it of change it if exists, or clear the key. "
        "You can also cancel the config command at any time."
    )

    GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(1, 5)

    def __init__(self):
        super().__init__()

        self.states.add_inline(self.START, "get", "Get")
        self.states.add_inline(self.START, "set", "Set")
        self.states.add_inline(self.START, "del", "Del")

        self.states.add_cancel_inline(self.GET_VAR)
        self.states.add_text(self.GET_VAR, "get_var")

        self.states.add_cancel_inline(self.SET_VAR)
        self.states.add_text(self.SET_VAR, "set_var")

        self.states.add_cancel_inline(self.DEL_VAR)
        self.states.add_text(self.DEL_VAR, "del_var")

        self.states.add_cancel_inline(self.SET_VALUE)
        self.states.add_text(self.SET_VALUE, "set_value")

    @store_update_context
    def get_handler(self):
        logger.debug("Requesting key name to get its value.")
        self.next(
            self.GET_VAR,
            "Tell me what key do you want to get.",
            self.builder.cancel_only,
        )

    @store_update_context
    def get_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            result = config[key]
        except (ValueError, KeyError) as e:
            if isinstance(e, ValueError):
                logger.debug("Key was invalid.")
                self.end(f"The key '{key}' is not a valid key.")
            else:
                logger.debug("Key doesn't exists.")
                self.end(f"The key '{key}' doesn't exists.")
        else:
            shown_result = quote_value_for_log(result)
            logger.debug(f"Replying with result {shown_result}.")
            self.end(f"The value for key '{key}' is '{result}'.")

    @store_update_context
    def set_handler(self):
        logger.debug("Requesting key name to set its value.")
        self.next(
            self.SET_VAR,
            "Tell me what key do you want to set.",
            reply_markup=self.builder.cancel_only,
        )

    @store_update_context
    def set_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            config[key]
        except ValueError:
            logger.debug("Can't set invalid config key 'invalid-key'.")
            self.end(f"The key '{key}' is not a valid key.")
        except KeyError:
            pass
        self.context_set("key", key)
        logger.debug("Requesting value to set the key.")
        self.next(
            self.SET_VALUE,
            f"Tell me what value do you want to put in the key '{key}'.",
            reply_markup=self.builder.cancel_only,
        )

    @store_update_context
    def set_value_handler(self):
        value = self.update.message.text
        shown_value = quote_value_for_log(value)
        logger.debug(f"Received value {shown_value}.")
        key = self.context_del("key")
        config[key] = value
        logger.debug(f"Stored {shown_value} in key '{key}'.")
        self.end("I'll remember that.")

    @store_update_context
    def del_handler(self):
        logger.debug("Requesting key name to clear its value.")
        self.next(
            self.DEL_VAR,
            "Tell me what key do you want to clear.",
            reply_markup=self.builder.cancel_only,
        )

    @store_update_context
    def del_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.debug(f"Received key name {shown_key}.")
        try:
            del config[key]
        except (ValueError, KeyError) as e:
            if isinstance(e, ValueError):
                logger.debug("Key was invalid.")
                self.end(f"The key '{key}' is not a valid key.")
            else:
                logger.debug("Key doesn't exists.")
                self.end(f"The key '{key}' doesn't exists.")
        else:
            logger.debug(f"Deleting config with key '{key}'.")
            self.end("I'll forget that.")
