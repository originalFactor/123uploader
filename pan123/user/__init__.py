from ..core import Client
from . import models, enums

__all__ = [
    "enums",
    "models",
    "User",
]


class User:
    def __init__(self, client: Client):
        self._client: Client = client

    async def info(self) -> models.UserInfoData:
        return await self._client.request(
            method="GET",
            endpoint="/api/v1/user/info",
            model=models.UserInfoData,
        )
