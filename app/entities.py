import enum


class GermanArticle(enum.Enum):
    no = ""
    der = "der"
    das = "das"
    die = "die"


class KnowledgeStatus(enum.Enum):
    article_right_first_time = "right in the first time"
    article_right_second_time = " right in the second time"
    article_right_third_time = "right in the third time"
    new_word_know = "known word"
    new_word_forgot = "forgot word"
