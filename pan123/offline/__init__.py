from ..core import Client
from . import models, enums

__all__ = ["models", "enums", "Offline"]


class Offline:
    def __init__(self, client: Client):
        self._client: Client = client
