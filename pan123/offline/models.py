__all__ = ["OfflineDownloadData", "OfflineDownloadProgressData"]

from ..models import BaseData
from .enums import *


class OfflineDownloadData(BaseData):
    taskID: int


class OfflineDownloadProgressData(BaseData):
    process: float
    status: OfflineDownloadProgressEnum
