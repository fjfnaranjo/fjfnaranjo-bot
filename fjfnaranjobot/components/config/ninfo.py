# TODO: Review all tests
# TODO: Generalize conversation end
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler

from fjfnaranjobot.command import (
    BotCommand,
    ConversationHandlerMixin,
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

    GET_VAR, SET_VAR, DEL_VAR, SET_VALUE = range(1, 5)

    def __init__(self):
        super().__init__()
        self.action_inlines = {
            "get": self.get_handler,
            "set": self.set_handler,
            "del": self.del_handler,
            "cancel": self.end,
        }
        self.states = {
            self.START: [
                CallbackQueryHandler(inline_handler(self.action_inlines, logger)),
            ],
            self.GET_VAR: [
                CallbackQueryHandler(inline_handler(self.cancel_inlines, logger)),
                MessageHandler(Filters.text, self.get_var_handler),
            ],
            self.SET_VAR: [
                CallbackQueryHandler(inline_handler(self.cancel_inlines, logger)),
                MessageHandler(Filters.text, self.set_var_handler),
            ],
            self.SET_VALUE: [
                CallbackQueryHandler(inline_handler(self.cancel_inlines, logger)),
                MessageHandler(Filters.text, self.set_value_handler),
            ],
            self.DEL_VAR: [
                CallbackQueryHandler(inline_handler(self.cancel_inlines, logger)),
                MessageHandler(Filters.text, self.del_var_handler),
            ],
        }

    @store_update_context
    def config_handler(self):
        logger.info("Entering 'config' conversation.")

        keyboard = [
            [
                InlineKeyboardButton("Get", callback_data="get"),
                InlineKeyboardButton("Set", callback_data="set"),
                InlineKeyboardButton("Delete", callback_data="del"),
            ],
            [InlineKeyboardButton("Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    @store_update_context
    def get_handler(self):
        logger.info("Requesting key name to get its value.")

        self.context.bot.edit_message_text(
            "Tell me what key do you want to get.",
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
            reply_markup=_cancel_markup,
        )
        return self.GET_VAR

    @store_update_context
    def get_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.info(f"Received key name {shown_key}.")

        try:
            result = config[key]
        except (ValueError, KeyError) as e:

            self.context.bot.delete_message(
                self.context.chat_data["chat_id"], self.context.chat_data["message_id"]
            )
            if isinstance(e, ValueError):
                logger.info("Key was invalid.")
                self.context.bot.send_message(
                    self.context.chat_data["chat_id"],
                    f"The key '{key}' is not a valid key.",
                )
            else:
                logger.info("Key doesn't exists.")
                self.context.bot.send_message(
                    self.context.chat_data["chat_id"],
                    f"The key '{key}' doesn't exists.",
                )
            self.end()

        else:

            shown_result = quote_value_for_log(result)
            logger.info(f"Replying with result {shown_result}.")

            self.context.bot.delete_message(
                self.context.chat_data["chat_id"], self.context.chat_data["message_id"]
            )
            self.context.bot.send_message(
                self.context.chat_data["chat_id"],
                f"The value for key '{key}' is '{result}'.",
            )
            self.end()

    @store_update_context
    def set_handler(self):
        logger.info("Requesting key name to set its value.")

        self.context.bot.edit_message_text(
            "Tell me what key do you want to set.",
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
            reply_markup=_cancel_markup,
        )
        return self.SET_VAR

    @store_update_context
    def set_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.info(f"Received key name {shown_key}.")

        try:
            config[key]
        except ValueError:

            logger.info("Can't set invalid config key 'invalid-key'.")

            self.context.bot.delete_message(
                self.context.chat_data["chat_id"],
                self.context.chat_data["message_id"],
            )
            self.context.bot.send_message(
                self.context.chat_data["chat_id"],
                f"The key '{key}' is not a valid key.",
            )
            self.end()

        except KeyError:
            pass

        self.context.chat_data["key"] = key

        logger.info("Requesting value to set the key.")

        self.context.bot.edit_message_text(
            f"Tell me what value do you want to put in the key '{key}'.",
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
            reply_markup=_cancel_markup,
        )
        return SET_VALUE

    @store_update_context
    def set_value_handler(self):
        value = self.update.message.text
        shown_value = quote_value_for_log(value)
        logger.info(f"Received value {shown_value}.")

        key = self.context.chat_data["key"]
        del self.context.chat_data["key"]
        config[key] = value

        logger.info(f"Stored {shown_value} in key '{key}'.")

        self.context.bot.delete_message(
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
        )
        self.context.bot.send_message(
            self.context.chat_data["chat_id"], "I'll remember that."
        )
        self.end()

    @store_update_context
    def del_handler(self):
        logger.info("Requesting key name to clear its value.")

        self.context.bot.edit_message_text(
            "Tell me what key do you want to clear.",
            self.context.chat_data["chat_id"],
            self.context.chat_data["message_id"],
            reply_markup=_cancel_markup,
        )
        return self.DEL_VAR

    @store_update_context
    def del_var_handler(self):
        key = self.update.message.text
        shown_key = quote_value_for_log(key)
        logger.info(f"Received key name {shown_key}.")

        try:
            del config[key]
        except (ValueError, KeyError) as e:

            self.context.bot.delete_message(
                self.context.chat_data["chat_id"], self.context.chat_data["message_id"]
            )
            if isinstance(e, ValueError):
                logger.info("Key was invalid.")
                self.context.bot.send_message(
                    self.context.chat_data["chat_id"],
                    f"The key '{key}' is not a valid key.",
                )
            else:
                logger.info("Key doesn't exists.")
                self.context.bot.send_message(
                    self.context.chat_data["chat_id"],
                    f"The key '{key}' doesn't exists.",
                )
            self.end()

        else:

            logger.info(f"Deleting config with key '{key}'.")

            self.context.bot.delete_message(
                self.context.chat_data["chat_id"], self.context.chat_data["message_id"]
            )
            self.context.bot.send_message(
                self.context.chat_data["chat_id"], "I'll forget that."
            )
            self.end()
