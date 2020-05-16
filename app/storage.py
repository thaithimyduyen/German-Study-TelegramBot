#!/usr/bin/env python3

import enum
import re
import sqlite3

from app.entities import GermanArticle


class CollectionName(enum.Enum):
    user = "user"
    top_1000 = "top1000"


class Word:
    def __init__(
        self,
        word,
        translation,
        article=None
    ):
        self._word = word
        self._translation = translation
        self._article = article

    def get_article(self) -> GermanArticle:
        return self._article

    def get_word(self) -> str:
        return self._word

    def get_translation(self) -> str:
        return self._translation

    def is_noun(self) -> bool:
        return self._article != ""


class WordsStorage:
    def __init__(
        self,
        file_db="words.db",
        init_sql="db.sql"
    ):
        self._file_db = file_db

        with self._open_conn() as conn:
            cursor = conn.cursor()
            with open(init_sql, 'r') as f:
                cursor.executescript(f.read())
            conn.commit()

    def _open_conn(self):
        return sqlite3.connect(database=self._file_db)

    def close(self):
        self._conn.close()

    def get_random_word(self, collection, user_id=None) -> Word:
        if collection != CollectionName.user:
            user_id = None

        with self._open_conn() as conn:
            rows = conn.cursor().execute(
                """
                SELECT "word", "translation", "article" FROM words
                WHERE "collection" = ? OR "user_id" = ?
                ORDER BY RANDOM()
                LIMIT 1;
                """,
                (collection.value, user_id)
            )

        try:
            row = next(rows)
        except StopIteration:
            return None

        return Word(
            word=row[0],
            translation=row[1],
            article=GermanArticle(row[2]),
        )

    def add_words(self, user_id, word_translations) -> bool:
        return True

    @staticmethod
    def parse_word_translation(word_translation):
        tokens = re.findall(
            pattern=r'^(der|das|die|)\s*(\w+)\s*-\s*(.+)$',
            string=word_translation,
            flags=re.UNICODE | re.IGNORECASE,
        )
        if len(tokens) == 0:
            raise Exception("invalid format")

        article, word, translation = tokens
        article = GermanArticle(article.lower())
        word = word.lower()
        if article != GermanArticle.no:  # Word is noun.
            word = word.capitalize()
        translation = translation.lower().capitalize()

        return Word(
            article=article,
            word=word,
            translation=translation
        )
