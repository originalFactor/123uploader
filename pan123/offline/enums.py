__all__ = ["OfflineDownloadProgressEnum"]

from enum import IntEnum


class OfflineDownloadProgressEnum(IntEnum):
    PROCESSING = 0
    FAILED = 1
    COMPLETED = 2
    RETRYING = 3
