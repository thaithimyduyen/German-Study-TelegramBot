#!/usr/bin/env python3

from app.gendercard import GenderCard
from app.entities import KnowledgeStatus
from app.knowledgecard import KnowledgeCard
from app.storage import CollectionName

KEY_USER_DATA_CARDS = "cards"
KEY_USER_DATA_COUNT = "count"
KEY_USER_DATA_COLLECTION = "collection"
KEY_USER_DATA_START = "fisrt_start_user"
KEY_USER_DATA_RESULT = "result_study"
COUNT = 20


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
        if KEY_USER_DATA_START not in context.user_data:
            self._view.send_message(
                update=update,
                text="Welcome to German-Study-Bot\n" +
                "/Start - to study with your lists of word\n" +
                "/Start1000 - to study with our lists of word"
            )
        else:
            self.create_card(
                update=update,
                context=context,
                user_id=update.effective_message.from_user.id,
            )
            context.user_data[KEY_USER_DATA_COUNT] = 1
        context.user_data[KEY_USER_DATA_START] = True

    def start1000(self, update, context):
        self.change_status_card(update, context)
        context.user_data[KEY_USER_DATA_COLLECTION] = CollectionName.top_1000

        self.create_card(
            update=update,
            context=context,
            user_id=update.effective_message.from_user.id,
        )

        context.user_data[KEY_USER_DATA_START] = True
        context.user_data[KEY_USER_DATA_COUNT] = 1

    def create_card(self, update, context, user_id):
        if context.user_data.get(KEY_USER_DATA_COUNT) == COUNT:
            result = context.user_data[KEY_USER_DATA_RESULT]
            text = (
                "_*Your result:*_\n\n" +
                "*Articles*:\n\n" +
                " - Right in first time: {} word(s)\n" +
                " - Right in second time: {} word(s)\n" +
                " - Right in third time: {} word(s)\n\n"
                "*New words*:\n\n" +
                " - Know: {} word(s)\n" +
                " - Forgot: {} word(s)\n"
            ).format(
                result[KnowledgeStatus.article_right_first_time.value],
                result[KnowledgeStatus.article_right_second_time.value],
                result[KnowledgeStatus.article_right_third_time.value],
                result[KnowledgeStatus.new_word_know.value],
                result[KnowledgeStatus.new_word_forgot.value]
            )
            self._view.send_message(
                update=update,
                text=text,
            )
            self._view.send_message(
                update=update,
                text="You complete session 🎉\n" +
                "/Start or /Start1000 to continue ➡️",
            )

            context.user_data[KEY_USER_DATA_COUNT] = 0
            self._clear_user_result(context)
            return
        name_collection = context.user_data[KEY_USER_DATA_COLLECTION]
        word = self._storage.get_random_word(name_collection, user_id)
        if word is None:
            self._view.send_message_reply(
                update=update,
                text="No words. Add words in format: `der Mann - Man`" +
                "\n\n*OR*\n\n" +
                "/Start1000 to begin with predefined words collection"
            )
            return

        is_noun = word.is_noun
        if is_noun:
            card = GenderCard(
                bot=self._bot,
                word=word,
                listener=TelegramBotCardEventListener(self),
            )
        else:
            card = KnowledgeCard(
                bot=self._bot,
                word=word,
                listener=TelegramBotCardEventListener(self),
            )

        if KEY_USER_DATA_COUNT not in context.user_data:
            context.user_data[KEY_USER_DATA_COUNT] = 0
        context.user_data[KEY_USER_DATA_COUNT] += 1

        message_id = card.start(update, context)

        cards = context.user_data.get(KEY_USER_DATA_CARDS, {})
        cards[message_id] = card
        context.user_data[KEY_USER_DATA_CARDS] = cards

    def _clear_user_result(self, context):
        context.user_data[KEY_USER_DATA_RESULT] = {
            KnowledgeStatus.article_right_first_time.value: 0,
            KnowledgeStatus.article_right_second_time.value: 0,
            KnowledgeStatus.article_right_third_time.value: 0,
            KnowledgeStatus.new_word_know.value: 0,
            KnowledgeStatus.new_word_forgot.value: 0
        }

    def knowledge_result(self, update, context, knowledge_status):
        if KEY_USER_DATA_RESULT not in context.user_data:
            self._clear_user_result(context)
        context.user_data[KEY_USER_DATA_RESULT][knowledge_status.value] += 1

    def card_button_clicked(self, update, context):
        dict_card = context.user_data.get(KEY_USER_DATA_CARDS, {})
        message_id = update.effective_message.message_id
        if message_id not in dict_card:
            return
        card = dict_card[message_id]
        card.button_clicked(update, context)

    def to_storage(self, update, context):
        user_id = str(update.effective_message.from_user.id)
        words = update.effective_message.text.split("\n")

        if self._storage.add_words_to_user_collection(user_id, words):
            self._view.send_message_reply(update, "Saved 🔖")
        else:
            self._view.send_message_reply(
                update=update,
                text="Invalid format\nCorrect format is `der Mann - Man`"
            )

    def delete_word(self, update, context):
        cards = context.user_data.get(KEY_USER_DATA_CARDS, {})
        collection = context.user_data.get(
            KEY_USER_DATA_COLLECTION,
            CollectionName.top_1000
        )
        if len(cards) == 0 or collection != CollectionName.user:
            self._view.send_message_reply(
                update=update,
                text="Can not delete last word"
            )
            return

        last_msg_id = max(cards)
        card = cards[last_msg_id]

        if card.is_old:
            self._view.send_message_reply(
                update=update,
                text="Current session has no cards to delete"
            )
            return

        if card.is_deleted():
            self._view.send_message_reply(
                update=update,
                text="Already deleted"
            )
            return

        word = card.get_word()
        user_id = update.effective_message.from_user.id

        self._storage.delete_word_from_user_collection(user_id, word)

        card.set_as_deleted(update, context)

        self._view.send_message_reply(
            update=update,
            text="Deleted",
            message_id=last_msg_id,
        )

        self.create_card(
            update=update,
            context=context,
            user_id=update.effective_message.from_user.id,
        )

    def delete_all(self, update, context):
        user_id = update.effective_message.from_user.id
        message_id = update.effective_message.message_id
        self._storage.delete_all_from_user_collection(user_id)
        self._view.send_message_reply(
            update=update,
            message_id=message_id,
            text="All words are deleted"
        )


class TelegramBotCardEventListener:
    def __init__(self, model):
        self._model = model

    def on_correct_answer_clicked(self, update, context, knowledge_status):
        self._model.knowledge_result(
            update=update,
            context=context,
            knowledge_status=knowledge_status
        )
        self._model.create_card(
            update=update,
            context=context,
            user_id=update.callback_query.from_user.id,
        )
