#!/usr/bin/env python3

import json

from app.entities import GermanArticle


class WordsStorage:
    def __init__(self, file_storage="words.json"):
        self._file_storage = file_storage
        with open(file_storage, 'r') as f:
            self._storage_data = json.load(f)

    def get_articles(self, user_id):
        get_words = {}
        dict_words = self._storage_data.get(
            str(user_id), {}).get(
                "articles", {}
        )
        for word, article_trans in dict_words.items():
            article, translator = article_trans
            get_words[word, translator] = GermanArticle(article)
        return get_words

    def _add_word_to_storage(self, user_id, word):
        word_tokens = word.split()

        if len(word_tokens) != 4:
            return False

        del word_tokens[2]

        article, word, translator = word_tokens

        article = article.lower()
        word = word.lower().capitalize()
        translator = translator.lower().capitalize()

        if article not in [
            GermanArticle.der.value,
            GermanArticle.die.value,
            GermanArticle.das.value
        ]:
            return False

        if user_id not in self._storage_data:
            self._storage_data[user_id] = {}

        if "articles" not in self._storage_data[user_id]:
            self._storage_data[user_id]["articles"] = {}

        self._storage_data[user_id]["articles"][word] = [article, translator]

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
