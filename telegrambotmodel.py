#!/usr/bin/env python3

import random

from gendercard import GenderCard

KEY_USER_DATA_CARDS = "cards"
KEY_USER_DATA_COUNT = "count"
COUNT_REPEAT = 20


class TelegramBotModel:
    def __init__(
        self,
        view,
        bot,
        storage,
        legal_users=["hedhyw", "makuzyenluca"],

    ):
        self._view = view
        self._legal_users = legal_users
        self._bot = bot
        self._storage = storage

    def create_gender_card(self, update, context, user_id):
        if context.user_data.get(KEY_USER_DATA_COUNT) == COUNT_REPEAT:
            self._view.send_message(
                update, context, "You complete session 🎉\n/Start to continue➡️"
            )
            context.user_data[KEY_USER_DATA_COUNT] = 0
            return
        word_articles = self._storage.get_articles(user_id)
        if len(word_articles) == 0:
            self._view.send_message_reply(update, context, "No words, /Start")
            return
        word_translation = random.choice(list(word_articles))
        word, translation = word_translation
        card = GenderCard(
            bot=self._bot,
            word=word,
            translation=translation,
            article=word_articles[word_translation],
            listener=TelegramBotCardEventListener(self),
        )

        if KEY_USER_DATA_COUNT not in context.user_data:
            context.user_data[KEY_USER_DATA_COUNT] = 0
        context.user_data[KEY_USER_DATA_COUNT] += 1

        message_id = card.model.start(update, context)

        cards = context.user_data.get(KEY_USER_DATA_CARDS, {})
        cards[message_id] = card
        context.user_data[KEY_USER_DATA_CARDS] = cards

    def start(self, update, context):
        if update.effective_user.username not in self._legal_users:
            self._view.send_message(update, "Enter password")
            return

        context.user_data.pop(KEY_USER_DATA_CARDS, None)

        self.create_gender_card(
            update, context, update.effective_message.from_user.id)

    def card_button_clicked(self, update, context):
        dict_card = context.user_data.get(KEY_USER_DATA_CARDS, {})
        message_id = update.effective_message.message_id
        if message_id not in dict_card:
            return
        card = dict_card[message_id]
        card.controller.button_clicked(update, context)

    def to_storage(self, update, context):
        user_id = str(update.effective_message.from_user.id)
        words = update.effective_message.text.split("\n")

        if len(words) > 1:
            added = self._storage.add_many_words(user_id, words)
        else:
            added = self._storage.add_word(user_id, words[0])

        if added:
            self._view.send_message_reply(update, context, "Saved 🔖")


class TelegramBotCardEventListener:
    def __init__(self, model):
        self._model = model

    def on_correct_answer_clicked(self, update, context):
        self._model.create_gender_card(
            update, context, update.callback_query.from_user.id)
