from telegram.messageentity import MessageEntity

from fjfnaranjobot.components.sorry.info import (
    logger,
    sorry_group_handler,
    sorry_handler,
)
from tests.base import CallWithMarkup

from ...base import BOT_USERNAME, BotHandlerTestCase


class SorryHandlersTests(BotHandlerTestCase):
    def _fake_user_mention(self, text, username, offset):
        self.set_string_command(text)
        self.set_entities(
            {
                MessageEntity(
                    type=MessageEntity.MENTION,
                    offset=offset,
                    length=len(username),
                    user=username,
                ): username
            }
        )

    def test_sorry_handler_processor(self):
        with self.assert_log_dispatch('Sending \'sorry\' back to the user.', logger):
            sorry_handler(*self.update_and_context)
        self.assert_reply_text('I don\'t know what to do about that. Sorry :(',)

    def test_sorry_group_handler_processor_bot(self):
        bot_mention = f'@{BOT_USERNAME}'
        bot_messages = [
            f'{bot_mention}',
            f'{bot_mention} some tail',
        ]
        for message in bot_messages:
            with self.subTest(message=message):
                self._fake_user_mention(message, bot_mention, message.find(bot_mention))
                with self.assert_log_dispatch(
                    'Sending \'sorry\' back to the user.', logger
                ):
                    sorry_group_handler(*self.update_and_context)
        self.assert_reply_calls(
            [
                CallWithMarkup('I don\'t know what to do about that. Sorry :('),
                CallWithMarkup('I don\'t know what to do about that. Sorry :('),
            ]
        )

    def test_sorry_group_handler_processor_not_bot(self):
        bot_mention = f'@{BOT_USERNAME}'
        not_bot_messages = [
            f'some header {bot_mention}',
            f'some header {bot_mention} some tail',
        ]
        for message in not_bot_messages:
            with self.subTest(message=message):
                self._fake_user_mention(message, bot_mention, message.find(bot_mention))
                assert None == sorry_group_handler(*self.update_and_context)
