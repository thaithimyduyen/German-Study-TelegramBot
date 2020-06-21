#!/usr/bin/env python3
from abc import ABC


class Card(ABC):
    @property
    def is_old(self):
        pass

    def set_as_deleted(self, update, context):
        pass

    def is_deleted(self) -> bool:
        pass

    def get_word(self):
        pass

    def start(self, update, context) -> str:
        pass

    def button_clicked(self, update, context):
        pass
