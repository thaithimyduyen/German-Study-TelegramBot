#!/usr/bin/env python3


from telegram import Bot
from telegram.utils.request import Request
from telegram.ext import Updater

from app.telegrambotmodel import TelegramBotModel
from app.telegrambotcontrol import TelegramBotController
from app.telegrambotview import TelegramBotViewer
from app.storage import WordsStorage


class StudyGermanTelegramBot:
    def __init__(
        self,
        token
    ):
        req = Request(con_pool_size=8)
        bot = Bot(token=token, request=req)
        storage = WordsStorage()
        self._updater = Updater(bot=bot, use_context=True)
        self._view = TelegramBotViewer(bot=bot)
        self._model = TelegramBotModel(
            view=self._view,
            bot=bot,
            storage=storage,
        )
        self._controller = TelegramBotController(self._model, self._updater)

    def run(self):
        self._updater.start_polling()
