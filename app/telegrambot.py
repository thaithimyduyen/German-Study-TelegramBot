#!/usr/bin/env python3

from telegram.utils.request import Request
from app.telegrambotmodel import TelegramBotModel
from app.telegrambotcontrol import TelegramBotController
from app.telegrambotview import TelegramBotViewer
from app.storage import WordsStorage
from telegram import Bot
from telegram.ext import Updater


class StudyGermanTelegramBot:
    def __init__(
        self,
        token="1087005171:AAG7TtgLFydcc4Z5WXrHd7m_XCssRjOLlJk",
        proxy_url="socks5://192.168.31.110:9100"
    ):
        req = Request(proxy_url=proxy_url, con_pool_size=8)
        bot = Bot(token=token, request=req)
        storage = WordsStorage()
        self._updater = Updater(bot=bot, use_context=True)
        self._view = TelegramBotViewer(bot=bot)
        self._model = TelegramBotModel(self._view, bot=bot, storage=storage,)
        self._controller = TelegramBotController(self._model, self._updater)

    def run(self):
        self._updater.start_polling()