from enum import Enum


class FileType(Enum):
    TEXT = ".txt"
    CSV = ".csv"
    JSON = ".json"

    def __str__(self):
        return self.value

    @property
    def mime_type(self):
        return {
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".json": "application/json"
        }[self.value]
