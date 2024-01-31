from enum import Enum


class ContextItemType(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    SETTING = "SETTING"

    def __str__(self):
        return self.value
