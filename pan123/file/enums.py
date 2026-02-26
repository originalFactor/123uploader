from enum import IntEnum

__all__ = [
    "CopyProgressEnum",
    "FileCategoryEnum",
]


class CopyProgressEnum(IntEnum):
    WAITING = 0
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3


class FileCategoryEnum(IntEnum):
    UNKNOWN = 0
    AUDIO = 1
    VIDEO = 2
    IMAGE = 3
    COMPRESSED = 10
