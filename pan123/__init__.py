__all__ = [
    "Pan123",
    "core",
    "exception",
    "log",
    "models",
    "file",
    "offline",
    "share",
    "user",
]

from types import TracebackType
from httpx import AsyncClient

from . import core, exception, log, models, file, offline, share, user


class Pan123:
    def __init__(
        self, client_id: str, client_secret: str, client: AsyncClient | None = None
    ):
        self._client: core.Client = core.Client(
            client_id=client_id,
            client_secret=client_secret,
            client=client,
        )
        self.user: user.User = user.User(client=self._client)
        self.files: file.File = file.File(client=self._client)
        self.offline: offline.Offline = offline.Offline(client=self._client)
        self.share: share.Share = share.Share(client=self._client)

    async def aclose(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        exc_tb: TracebackType | None,
    ):
        await self.aclose()
