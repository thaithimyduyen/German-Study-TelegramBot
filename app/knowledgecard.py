import logging
import enum
import copy

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode
)
import telegram.error


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class KnowledgeCard:
    def __init__(self, bot, word, listener):
        self._view = KnowledgeCardView(bot)
        self._model = KnowledgeCardModel(
            view=self._view,
            word=word,
            listener=listener,
        )
        self._controller = KnowledgeCardController(self._model)
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


class Knowledge(enum.Enum):
    true = "✅"
    false = "❌"


class KnowledgeCardModel:
    def __init__(self, view, word, listener):
        self._view = view
        self._word = word
        self._listener = listener
        self._message_id = None
        self.is_old = False

    def start(self, update, context) -> str:
        self._message_id = self._view.send_card(
            update=update,
            word=self._word,
            translation=None,
        )
        return self._message_id

    def show_translation(self, update, context, knowledge):
        self._view.update_card(
            update=update,
            translation=self._word.get_translation() + " " + knowledge.value,
        )
        self._listener.on_correct_answer_clicked(update, context)

    def set_as_deleted(self, update, context):
        self._view.update_card_as_deleted(
            update=update,
            context=context,
            message_id=self._message_id,
        )
        self._is_deleted = True


class KnowledgeCardController:
    def __init__(self, model):
        self._model = model

    def button_clicked(self, update, context):
        query_data = update.callback_query.data
        if query_data == "know":
            self._model.show_translation(
                update=update,
                context=context,
                knowledge=Knowledge.true,
            )
        elif query_data == "forgot":
            self._model.show_translation(
                update=update,
                context=context,
                knowledge=Knowledge.false,
            )


class KnowledgeCardView:
    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    def _get_card_markup(translation=None):

        keyboard = [[
            InlineKeyboardButton(
                text="Know " + Knowledge.true.value,
                callback_data="know"
            ),
            InlineKeyboardButton(
                text="Forgot " + Knowledge.false.value,
                callback_data="forgot"
            ),
        ]]
        if translation is not None:
            keyboard.pop(0)
            keyboard.append([
                InlineKeyboardButton(
                    text=translation,
                    callback_data="translation")
            ])

        return InlineKeyboardMarkup(keyboard)

    def send_card(self, update, word, translation):
        markup = KnowledgeCardView._get_card_markup(
            translation=translation,
        )
        return self._bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="*"+word.get_word()+"*",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        ).message_id

    def update_card(self, update, translation):
        reply_markup = KnowledgeCardView._get_card_markup(
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
