# TODO: Review all tests
from fjfnaranjobot.command import (
    BotCommand,
    ConversationHandlerMixin,
    MarkupBuilder,
    StateSet,
    store_update_context,
)
from fjfnaranjobot.common import inline_handler, quote_value_for_log
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
    builder = MarkupBuilder()

    GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(4)

    def build(self):
        states = StateSet(self)

        states.add_cancel_inline(self.START)
        states.add_inline(self.START, "get", "Get")
        states.add_inline(self.START, "set", "Set")
        states.add_inline(self.START, "del", "Del")
        self.initial_markup = self.builder.from_inlines(
            states.inlines_captions(self.START)
        )

        states.add_cancel_inline(self.GET_VAR)
        states.add_text(self.GET_VAR, "get_var")

        states.add_cancel_inline(self.SET_VAR)
        states.add_text(self.SET_VAR, "set_var")

        states.add_cancel_inline(self.DEL_VAR)
        states.add_text(self.DEL_VAR, "del_var")

        states.add_cancel_inline(self.SET_VALUE)
        states.add_text(self.SET_VALUE, "set_value")

        return states.all_states

    @store_update_context
    def get_handler(self):
        logger.debug("Requesting key name to get its value.")
        self.edit_message(
            "Tell me what key do you want to get.",
            self.builder.cancel_only,
        )
        return self.GET_VAR

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
        self.edit_message(
            "Tell me what key do you want to set.",
            reply_markup=self.builder.cancel_only,
        )
        return self.SET_VAR

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
        self.remember("key", key)
        logger.debug("Requesting value to set the key.")
        self.edit_message(
            f"Tell me what value do you want to put in the key '{key}'.",
            reply_markup=self.builder.cancel_only,
        )
        return SET_VALUE

    @store_update_context
    def set_value_handler(self):
        value = self.update.message.text
        shown_value = quote_value_for_log(value)
        logger.debug(f"Received value {shown_value}.")
        key = self.context.chat_data["key"]
        del self.context.chat_data["key"]
        config[key] = value
        logger.debug(f"Stored {shown_value} in key '{key}'.")
        self.end("I'll remember that.")

    @store_update_context
    def del_handler(self):
        logger.debug("Requesting key name to clear its value.")
        self.edit_message(
            "Tell me what key do you want to clear.",
            reply_markup=_cancel_markup,
        )
        return self.DEL_VAR

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
