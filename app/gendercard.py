#!/usr/bin/env python3

import logging
import enum
import copy

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode
)
import telegram.error

from app.entities import GermanArticle, KnowledgeStatus
from app.card import Card
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class GenderCard(Card):
    def __init__(self, bot, word, listener):
        self._view = GenderCardView(bot)
        self._model = GenderCardModel(
            view=self._view,
            word=word,
            listener=listener,
        )
        self._controller = GenderCardController(self._model)
        self._is_deleted = False

    def set_old(self):
        self._model.is_old = True

    @property
    def is_old(self):
        return self._model.is_old

    def set_as_deleted(self, update, context):
        self._model.set_as_deleted(update, context)

    def is_deleted(self) -> bool:
        return self._is_deleted

    def get_word(self):
        return copy.copy(self._model._word)

    def start(self, update, context) -> str:
        return self._model.start(update, context)

    def button_clicked(self, update, context):
        self._controller.button_clicked(update, context)


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
        self._message_id = None
        self.is_old = False
        self._knowledge_status_count = 0

    def start(self, update, context) -> str:
        self._message_id = self._view.send_card(
            update=update,
            word=self._word,
            articles=self._articles,
            translation=self._visible_translation,
        )
        return self._message_id

    def check_answer(self, update, context, article):
        if self._right_answer:
            return
        self._right_answer = article == self._word.get_article()
        self._articles = {
            article: Answers.true if self._right_answer else Answers.false,
        }
        self._view.update_card(
            update=update,
            articles=self._articles,
            translation=self._visible_translation,
        )
        self._knowledge_status_count += 1
        if self._knowledge_status_count == 1:
            knowledge_status = KnowledgeStatus.article_right_first_time
        elif self._knowledge_status_count == 2:
            knowledge_status = KnowledgeStatus.article_right_second_time
        elif self._knowledge_status_count == 3:
            knowledge_status = KnowledgeStatus.article_right_third_time

        if self._right_answer and not self.is_old:
            self._listener.on_correct_answer_clicked(
                update=update,
                context=context,
                knowledge_status=knowledge_status
            )

    def show_translation(self, update, context):
        if self._visible_translation is not None:
            return
        self._visible_translation = self._word.get_translation()
        self._view.update_card(
            update=update,
            articles=self._articles,
            translation=self._visible_translation,
        )

    def set_as_deleted(self, update, context):
        self._view.update_card_as_deleted(
            update=update,
            context=context,
            message_id=self._message_id,
        )
        self._is_deleted = True


class GenderCardController:
    def __init__(self, model):
        self._model = model

    def button_clicked(self, update, context):
        query_data = update.callback_query.data
        if query_data == "translation":
            self._model.show_translation(update, context)
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
                callback_data="translation",
            )
        ]]

        return InlineKeyboardMarkup(keyboard)

    def send_card(self, update, word, articles, translation):
        markup = GenderCardView._get_card_markup(
            articles=articles,
            translation=translation,
        )
        return self._bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="*"+word.get_word()+"*",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        ).message_id

    def update_card(self, update, articles, translation):
        reply_markup = GenderCardView._get_card_markup(
            articles=articles,
            translation=translation,
        )
        try:
            return self._bot.edit_message_reply_markup(
                chat_id=update.effective_message.chat_id,
                message_id=update.effective_message.message_id,
                reply_markup=reply_markup
            )
        except telegram.error.BadRequest:
            return None

    def update_card_as_deleted(self, update, context, message_id):
        return self._bot.edit_message_reply_markup(
            chat_id=update.effective_message.chat_id,
            message_id=message_id,
            reply_markup=None
        )
