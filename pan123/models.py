# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from datetime import datetime, date, time
from types import NoneType
from typing import TypeVar, Generic, Annotated

from pydantic import BaseModel, field_validator, Field

__all__ = ["BaseData", "AccessTokenData", "DataT", "APIReturn"]


class BaseData(BaseModel): ...


class AccessTokenData(BaseData):
    accessToken: str
    expiredAt: datetime


class IPForbideSwitchData(BaseData):
    Done: bool


class ForbiddenIPListData(BaseData):
    ipList: list[str]
    status: bool

    @field_validator("status", mode="before")
    @classmethod
    def _validate_status(cls, value: int) -> bool:
        return bool(value - 2)


class DatetimeRange(BaseModel):
    start: datetime
    end: datetime


class DirectLinkOfflineLogItem(BaseModel):
    id: str
    fileName: str
    fileSize: int
    logTimeRange: DatetimeRange
    downloadURL: str

    @field_validator("logTimeRange", mode="before")
    @classmethod
    def _validate_log_time_range(cls, value: str) -> DatetimeRange:
        date_str, time_str = value.split(" ")
        start_str, end_str = time_str.split("~")

        date_obj = date.fromisoformat(date_str)
        start_time = time.fromisoformat(start_str)
        end_time = time.fromisoformat(end_str)
        start_obj = datetime.combine(date_obj, start_time)
        end_obj = datetime.combine(date_obj, end_time)

        return DatetimeRange(start=start_obj, end=end_obj)


class DirectLinkOfflineLogData(BaseData):
    total: int
    list: list[DirectLinkOfflineLogItem]


class DirectLinkTrafficLogItem(BaseModel):
    uniqueID: str
    fileName: str
    fileSize: int
    filePath: str
    directLinkURL: str
    fileSource: int
    totalTraffic: int


class DirectLinkTrafficLogData(BaseData):
    total: int
    list: list[DirectLinkTrafficLogItem]


class EnableDirectLinkData(BaseData):
    filename: str


class DirectLinkUrlData(BaseData):
    url: str


class DisableDirectLinkData(BaseData):
    filename: str


class OSSMkdirItem(BaseModel):
    filename: str
    dirID: str


class OSSMkdirData(BaseData):
    list: list[OSSMkdirItem]


DataT = TypeVar("DataT", bound=(BaseData | NoneType))


class APIReturn(BaseModel, Generic[DataT]):
    code: int
    message: str
    data: DataT | None
    xTraceID: Annotated[str, Field(validation_alias="x-traceID")]
