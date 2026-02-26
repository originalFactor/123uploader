__all__ = ["VipInfo", "DeveloperInfo", "UserInfoData"]

from datetime import datetime
from pydantic import BaseModel

from ..models import BaseData
from .enums import VipLevelEnum


class VipInfo(BaseModel):
    vipLevel: VipLevelEnum
    vipLabel: str
    startTime: datetime
    endTime: datetime


class DeveloperInfo(BaseModel):
    startTime: datetime
    endTime: datetime


class UserInfoData(BaseData):
    uid: int
    nickname: str
    headImage: str
    passport: str
    mail: str
    spaceUsed: int
    spacePermanent: int
    spaceTemp: int
    spaceTempExpr: datetime
    vip: bool
    directTraffic: int
    isHideUID: bool
    httpsCount: int
    vipInfo: list[VipInfo] | None = None
    developerInfo: DeveloperInfo | None = None
