#!/usr/bin/env python3

from telegram import ParseMode, ReplyKeyboardMarkup

CUSTOM_KEYBOARD = [
    ["/start", "/start1000", "/delete", "/delete_all"]
]


class TelegramBotViewer:
    def __init__(self, bot):
        self._bot = bot

    def send_message_reply(
        self,
        update,
        text,
        message_id=None,
    ):
        if message_id is None:
            message_id = update.effective_message.message_id
        reply_markup = ReplyKeyboardMarkup(
            CUSTOM_KEYBOARD, resize_keyboard=True)
        self._bot.send_message(
            reply_to_message_id=message_id,
            chat_id=update.effective_message.chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )

    def send_message(self, update, text):
        reply_markup = ReplyKeyboardMarkup(
            CUSTOM_KEYBOARD, resize_keyboard=True)
        self._bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
