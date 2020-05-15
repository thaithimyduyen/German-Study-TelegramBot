#!/usr/bin/env python3

import json
import enum

from app.entities import GermanArticle


class CollectionName(enum.Enum):
    user = "User Collection"
    top_1000 = "1000 words collection"


class WordsStorage:
    def __init__(
        self,
        file_storage_user="words.json",
        file_storage_1000="1000_words.json",
    ):
        self.file_storage_user = file_storage_user
        with open(file_storage_user, 'r') as f:
            self._storage_data_user = json.load(f)
        self.file_storage_1000 = file_storage_1000
        with open(file_storage_1000, 'r') as f:
            self._storage_data_1000 = json.load(f)

    def get_words_dict(self, user_id, name_collection):
        get_words = {}
        if name_collection == CollectionName.user:
            dict_words = self._storage_data_user.get(str(user_id), {})
        else:
            dict_words = self._storage_data_1000.get("0", {})
        for word, article_trans in dict_words.items():
            article = article_trans.get("article", "")
            translation = article_trans.get("translation", "")
            get_words[word, translation] = GermanArticle(article)
        return get_words

    def _add_word_to_storage(self, user_id, word):
        word_tokens = word.split()

        if len(word_tokens) != 4:
            return False

        del word_tokens[2]

        article, word, translation = word_tokens

        article = article.lower()
        word = word.lower().capitalize()
        translation = translation.lower().capitalize()

        if article not in [
            GermanArticle.der.value,
            GermanArticle.die.value,
            GermanArticle.das.value
        ]:
            return False

        if user_id not in self._storage_data:
            self._storage_data[user_id] = {}

        self._storage_data[user_id][word] = {
            "article": article,
            "transaltion": translation,
        }

        return True

    def add_word(self, user_id, word) -> bool:
        added = self._add_word_to_storage(user_id, word)
        self._save()
        return added

    def add_many_words(self, user_id, words) -> bool:
        added = False
        for word in words:
            added |= self._add_word_to_storage(user_id, word)
        self._save()
        return added

    def _save(self):
        with open(self._file_storage, 'w') as f:
            json.dump(self._storage_data, f)
