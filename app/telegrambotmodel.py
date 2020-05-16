#!/usr/bin/env python3


from app.gendercard import GenderCard
from app.storage import CollectionName

KEY_USER_DATA_CARDS = "cards"
KEY_USER_DATA_COUNT = "count"
KEY_USER_DATA_COLLECTION = "collection"
COUNT_REPEAT = 20


class TelegramBotModel:
    def __init__(
        self,
        view,
        bot,
        storage,
    ):
        self._view = view
        self._bot = bot
        self._storage = storage

    def change_status_card(self, update, context):
        for _, card in context.user_data.get(KEY_USER_DATA_CARDS, {}).items():
            card.set_old()

    def start(self, update, context):
        self.change_status_card(update, context)
        context.user_data[KEY_USER_DATA_COLLECTION] = CollectionName.user
        self.create_gender_card(
            update=update,
            context=context,
            user_id=update.effective_message.from_user.id
        )

    def start1000(self, update, context):
        self.change_status_card(update, context)
        context.user_data[KEY_USER_DATA_COLLECTION] = CollectionName.top_1000
        self.create_gender_card(
            update=update,
            context=context,
            user_id=update.effective_message.from_user.id,
        )

    def create_gender_card(self, update, context, user_id):
        if context.user_data.get(KEY_USER_DATA_COUNT) == COUNT_REPEAT:
            self._view.send_message(
                update=update,
                context=context,
                text="You complete session 🎉\n" +
                "/Start or /Start1000 to continue ➡️",
            )
            context.user_data[KEY_USER_DATA_COUNT] = 0
            return

        name_collection = context.user_data.get(
            KEY_USER_DATA_COLLECTION, CollectionName.user
        )
        word = self._storage.get_random_word(name_collection, user_id)
        if word is None:
            self._view.send_message_reply(
                update=update,
                context=context,
                text="No words. Add words in format: `der Mann - Man`" +
                "\n\n*OR*\n\n" +
                "/Start1000 to begin with predefined words collection"
            )
            return
        card = GenderCard(
            bot=self._bot,
            word=word,
            listener=TelegramBotCardEventListener(self),
        )

        if KEY_USER_DATA_COUNT not in context.user_data:
            context.user_data[KEY_USER_DATA_COUNT] = 0
        context.user_data[KEY_USER_DATA_COUNT] += 1

        message_id = card.model.start(update, context)

        cards = context.user_data.get(KEY_USER_DATA_CARDS, {})
        cards[message_id] = card
        context.user_data[KEY_USER_DATA_CARDS] = cards

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
            update=update,
            context=context,
            user_id=update.callback_query.from_user.id,
        )
