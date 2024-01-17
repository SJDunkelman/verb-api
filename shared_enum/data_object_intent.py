from enum import Enum


class Intent(Enum):
    COMPLETE = 'COMPLETE'
    AMEND = 'AMEND'
    RETRIEVE = 'RETRIEVE'
    SAMPLE = 'SAMPLE'

    def __str__(self):
        return self.value
