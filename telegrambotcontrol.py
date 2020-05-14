#!/usr/bin/env python3

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)


class TelegramBotController:
    def __init__(self, model, updater):
        self._model = model

        updater.dispatcher.add_handler(
            CommandHandler('start', self._handle_start)
        )
        updater.dispatcher.add_handler(
            CallbackQueryHandler(self._handle_button_clicked)
        )
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & (~Filters.command),
                self._handle_text
            )
        )

    def _handle_start(self, update, context):
        self._model.start(update, context)

    def _handle_button_clicked(self, update, context):
        self._model.card_button_clicked(update, context)

    def _handle_text(self, update, context):
        self._model.to_storage(update, context)
