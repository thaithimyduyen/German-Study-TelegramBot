#!/usr/bin/env python3

from telegram import ParseMode


class TelegramBotViewer:
    def __init__(self, bot):
        self._bot = bot

    def send_message_reply(self, update, context, text):
        self._bot.send_message(
            reply_to_message_id=update.effective_message.message_id,
            chat_id=update.effective_message.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )

    def send_message(self, update, context, text):
        self._bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
        )
