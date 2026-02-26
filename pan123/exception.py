__all__ = ["ClientException"]

from typing import Generic

from httpx import Request

from .models import APIReturn, DataT


class ClientException(RuntimeError, Generic[DataT]):
    def __init__(self, request: Request, response: APIReturn[DataT]):
        self.request: Request = request
        self.response: APIReturn[DataT] = response
        super().__init__(
            f"{self.request.url} failed with {self.response.code}: {self.response.message}"
        )
