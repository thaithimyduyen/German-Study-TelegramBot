#!/usr/bin/env python3

import logging
import enum

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode
)

from app.entities import GermanArticle

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class GenderCard:
    def __init__(self, bot, word, listener):
        self.view = GenderCardView(bot)
        self.model = GenderCardModel(
            view=self.view,
            word=word,
            listener=listener,
        )
        self.controller = GenderCardController(self.model)

    def set_old(self):
        self.model.is_old = True


class Answers(enum.Enum):
    true = "✅"
    false = "❌"
    none = "☐"


class GenderCardModel:
    def __init__(self, view, word, listener):
        self._view = view
        self._word = word
        self._visible_translation = None
        self._right_answer = False
        self._listener = listener
        self._articles = {}

        self.is_old = False

    def start(self, update, context):
        return self._view.send_card(
            update=update,
            text=self._word.get_word(),
            articles=self._articles,
            translation=self._visible_translation,
        )

    def check_answer(self, update, context, article):
        if self._right_answer:
            return
        self._right_answer = article == self._word.get_article()
        self._articles = {
            article: Answers.true if self._right_answer else Answers.false,
        }
        self._view.update_card(update, self._articles,
                               self._visible_translation)

        if self._right_answer:
            if not self.is_old:
                self._listener.on_correct_answer_clicked(
                    update=update,
                    context=context,
                )

    def show_transaltion(self, update, context):
        if self._visible_translation is not None:
            return
        self._visible_translation = self._word.get_translation()
        self._view.update_card(
            update=update,
            articles=self._articles,
            translation=self._visible_translation,
        )


class GenderCardController:
    def __init__(self, model):
        self._model = model

    def button_clicked(self, update, context):
        query_data = update.callback_query.data
        if query_data == "translation":
            self._model.show_transaltion(update, context)
        else:
            self._model.check_answer(
                update=update,
                context=context,
                article=GermanArticle(query_data),
            )


class GenderCardView:
    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    def _get_card_markup(articles, translation):
        def get_text(article):
            return article.value + " " + \
                articles.get(article, Answers.none).value

        translation_text = translation
        if translation is None:
            translation_text = "Show translation"

        keyboard = [[
            InlineKeyboardButton(
                text=get_text(GermanArticle.der),
                callback_data=GermanArticle.der.value
            ),
            InlineKeyboardButton(
                text=get_text(GermanArticle.das),
                callback_data=GermanArticle.das.value
            ),
            InlineKeyboardButton(
                text=get_text(GermanArticle.die),
                callback_data=GermanArticle.die.value
            )
        ], [
            InlineKeyboardButton(
                text=translation_text,
                callback_data="translation")
        ]]

        return InlineKeyboardMarkup(keyboard)

    def send_card(self, update, text, articles, translation):
        return self._bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="*"+text+"*",
            reply_markup=GenderCardView._get_card_markup(
                articles, translation),
            parse_mode=ParseMode.MARKDOWN
        ).message_id

    def update_card(self, update, articles, translation):
        return self._bot.edit_message_reply_markup(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            reply_markup=GenderCardView._get_card_markup(articles, translation)
        )
