__all__ = [
    "CreateShareData",
    "BaseShareLinkItem",
    "ShareLinkItem",
    "PaidShareLinkItem",
    "ListShareData",
    "ShareItemT",
]

from datetime import datetime
from typing import TypeVar, Generic
from pydantic import BaseModel, field_validator
from ..models import BaseData
from .enums import *


class CreateShareData(BaseData):
    shareID: int
    shareKey: str


class BaseShareLinkItem(BaseModel):
    shareId: int
    shareKey: str
    shareName: str
    expiration: datetime
    expired: bool
    trafficSwitch: TrafficSwitchEnum
    trafficLimitSwitch: bool
    trafficLimit: int
    bytesCharge: int
    previewCount: int
    downloadCount: int
    saveCount: int

    @field_validator("trafficLimitSwitch", mode="before")
    @classmethod
    def validate_traffic_limit_switch(cls, value: int) -> bool:
        return bool(value - 1)


class ShareLinkItem(BaseShareLinkItem):
    sharePwd: str


class PaidShareLinkItem(BaseShareLinkItem):
    payAmount: float
    amount: float


ShareItemT = TypeVar("ShareItemT", bound=BaseShareLinkItem)


class ListShareData(BaseData, Generic[ShareItemT]):
    lastShareId: int
    shareList: list[ShareItemT]
