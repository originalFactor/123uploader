__all__ = ["Client"]

from ssl import PROTOCOL_TLS_CLIENT
from datetime import datetime, UTC
from typing import cast

from httpx import AsyncClient, Response
from httpx._types import QueryParamTypes, RequestData, RequestFiles
from truststore import SSLContext

from .log import logger
from .models import DataT, APIReturn, AccessTokenData
from .exception import ClientException

HEADERS = {"Platform": "open_platform"}


class Client:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        client: AsyncClient | None = None,
        storage_file: str | None = "access_token.json",
    ):
        self.base_url: str = "https://open-api.123pan.com"
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self._client: AsyncClient = client or AsyncClient(
            verify=SSLContext(PROTOCOL_TLS_CLIENT)
        )
        self._hold_client: bool = client is None
        self.storage_file: str | None = storage_file
        self._access_token: str = ""
        self._access_token_expires: datetime = datetime.min.replace(tzinfo=UTC)

    async def request_raw(
        self,
        method: str,
        endpoint: str,
        params: QueryParamTypes | None = None,
        json: object = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        use_access_token: bool = True,
        no_platform_header: bool = False,
        base_url: str | None = None,
    ) -> Response:
        headers = HEADERS.copy()
        if base_url is None:
            base_url = self.base_url
        if use_access_token:
            headers["Authorization"] = f"Bearer {await self._get_access_token()}"
        if no_platform_header:
            _ = headers.pop("Platform", None)

        response = await self._client.request(
            method=method,
            url=f"{base_url}{endpoint}",
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
        )

        request = response.request
        logger.debug(
            f"REQUEST BODY = {request.read()}\n" + f"RESPONSE BODY = {response.read()}"
        )

        return response.raise_for_status()

    async def request(
        self,
        method: str,
        endpoint: str,
        model: type[DataT],
        params: QueryParamTypes | None = None,
        json: object = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        use_access_token: bool = True,
        no_platform_header: bool = False,
        base_url: str | None = None,
    ) -> DataT:
        response = await self.request_raw(
            method=method,
            endpoint=endpoint,
            params=params,
            json=json,
            data=data,
            files=files,
            use_access_token=use_access_token,
            no_platform_header=no_platform_header,
            base_url=base_url,
        )

        ret = APIReturn[model].model_validate_json(response.content)
        if ret.code != 0:
            raise ClientException[model](response.request, ret)
        return cast(DataT, ret.data)

    def get_client(self) -> AsyncClient:
        return self._client

    def _is_access_token_valid(self) -> bool:
        return self._access_token_expires.astimezone(UTC) > datetime.now(UTC)

    def _load_access_token(self) -> bool:
        if self._is_access_token_valid():
            return True
        if self.storage_file is None:
            return False
        try:
            with open(self.storage_file, "r") as f:
                data = AccessTokenData.model_validate_json(f.read())
            self._access_token = data.accessToken
            self._access_token_expires = data.expiredAt
            return self._is_access_token_valid()
        except FileNotFoundError:
            pass
        return False

    def _save_access_token(self, data: AccessTokenData) -> None:
        self._access_token = data.accessToken
        self._access_token_expires = data.expiredAt
        if self.storage_file is None:
            return
        with open(self.storage_file, "w") as f:
            _ = f.write(data.model_dump_json())

    async def _get_access_token(self) -> str:
        if not self._load_access_token():
            await self._update_access_token()
        return self._access_token

    async def _update_access_token(self) -> None:
        data = await self.request(
            method="POST",
            endpoint="/api/v1/access_token",
            model=AccessTokenData,
            json={
                "clientID": self.client_id,
                "clientSecret": self.client_secret,
            },
            use_access_token=False,
        )
        self._save_access_token(data)

    async def aclose(self) -> None:
        if self._hold_client:
            await self._client.aclose()
