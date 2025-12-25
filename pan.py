# Copyright (C) 2025 originalFactor
#
# This file is part of autouploader.
#
# autouploader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autouploader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with autouploader.  If not, see <https://www.gnu.org/licenses/>.

"""
123pan api abstract
"""

import asyncio
from datetime import datetime, timezone
from math import ceil
from os.path import isfile, getsize, join
import json
import random
import string
from typing import Awaitable, Callable
from httpx import AsyncClient
import truststore
import ssl
from enum import Enum
from globals import CURR_DIR
from configuration import config
from pwsh import pwsh_md5, pwsh_rmdir, pwsh_splitfile, pwsh_run


class SpecialActions(Enum):
    DELETE = random.choices(string.hexdigits, k=16)


class PanAPIError(Exception):
    pass


BASE_URL = "https://open-api.123pan.com"
HEADERS = {"Platform": "open_platform", "Content-Type": "application/json"}

PAN_CLIENT_ID: str = config.get("123ClientId")
PAN_CLIENT_SECRET: str = config.get("123ClientSecret")
assert PAN_CLIENT_ID, "123ClientId not found in config.json"
assert PAN_CLIENT_SECRET, "123ClientSecret not found in config.json"


client = AsyncClient(verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))

_pan_access_token: str | None = None
_pan_access_token_expires: datetime | None = None

if isfile(join(CURR_DIR, "access_token.json")):
    with open(join(CURR_DIR, "access_token.json"), "r") as f:
        access_token: dict = json.load(f)
        _pan_access_token = access_token["accessToken"]
        _pan_access_token_expires = datetime.fromisoformat(access_token["expiredAt"])


async def get_headers(**kwargs) -> dict:
    result = {
        **HEADERS,
        "Authorization": f"Bearer {await get_pan_access_token()}",
    }

    for k, v in kwargs.items():
        _k = k.replace("__", "-")
        if v == SpecialActions.DELETE:
            del result[_k]
        else:
            result[_k] = v

    return result


async def request_pan(
    endpoint: str,
    method: str = "GET",
    headers: dict | Callable[[], Awaitable[dict]] = get_headers,
    params: dict | None = None,
    json: dict | None = None,
) -> dict:
    response = await client.request(
        method,
        f"{BASE_URL}{endpoint}",
        headers=await headers() if callable(headers) else headers,
        params=params,
        json=json,
    )
    response.raise_for_status()
    resp: dict = response.json()
    if resp.get("code") != 0:
        raise PanAPIError(f"Failed to request {endpoint}: {resp.get('message')}")
    return resp["data"]


async def get_pan(*args, **kwargs) -> dict:
    return await request_pan(*args, method="GET", **kwargs)


async def post_pan(*args, **kwargs) -> dict:
    return await request_pan(*args, method="POST", **kwargs)


async def update_pan_access_token() -> None:
    global _pan_access_token, _pan_access_token_expires
    endpoint = f"/api/v1/access_token"
    data = await post_pan(
        endpoint,
        headers=HEADERS,
        json={
            "clientID": PAN_CLIENT_ID,
            "clientSecret": PAN_CLIENT_SECRET,
        },
    )
    _pan_access_token = data["accessToken"]
    _pan_access_token_expires = datetime.fromisoformat(data["expiredAt"])
    with open(join(CURR_DIR, "access_token.json"), "w") as f:
        json.dump(data, f)


async def get_pan_access_token() -> str:
    if (
        _pan_access_token is None
        or _pan_access_token_expires is None
        or datetime.now(timezone.utc) >= _pan_access_token_expires
    ):
        await update_pan_access_token()
    assert _pan_access_token
    return _pan_access_token


async def create_file(
    filename: str,
    etag: str,
    size: int,
    contain_dir: bool = False,
    parent_id: int = 0,
    duplicate: int = 1,
) -> dict:
    endpoint = f"/upload/v2/file/create"
    data = await post_pan(
        endpoint,
        json={
            "parentFileID": parent_id,
            "filename": filename,
            "etag": etag,
            "size": size,
            "duplicate": duplicate,
            "containDir": contain_dir,
        },
    )
    return data


async def upload_slice(
    base_url: str, preupload_id: str, slice_no: int, slice_md5: str, slice_path: str
) -> bool:
    endpoint = f"{base_url}/upload/v2/file/slice"
    with open(slice_path, "rb") as f:
        response = await client.post(
            endpoint,
            headers=await get_headers(Content__Type=SpecialActions.DELETE),
            data={
                "preuploadID": preupload_id,
                "sliceNo": slice_no,
                "sliceMD5": slice_md5,
            },
            files={"slice": f},
        )
        response.raise_for_status()

    return response.json().get("code") == 0


async def verify_complete(preupload_id: str) -> int:
    endpoint = f"/upload/v2/file/upload_complete"
    try:
        data = await post_pan(
            endpoint,
            json={
                "preuploadID": preupload_id,
            },
        )
    except PanAPIError as e:
        return -1
    return data.get("fileID", -1)


async def upload(local_path: str, remote_path: str) -> int:
    remote_path = remote_path.replace("\\", "/")
    local_path = local_path.replace("\\", "/")
    md5 = await pwsh_md5(local_path)
    size = getsize(local_path)
    create_result = await create_file(
        filename=remote_path,
        etag=md5,
        size=size,
        contain_dir=True,
    )
    if create_result.get("reuse"):
        fileID = create_result["fileID"]
        assert isinstance(fileID, int)
        return fileID

    preupload_id = create_result["preuploadID"]
    assert isinstance(preupload_id, str)
    base_url = random.choice(create_result["servers"])
    assert isinstance(base_url, str)

    slice_size = create_result["sliceSize"]
    assert isinstance(slice_size, int)
    slices = ceil(size / slice_size)
    tmp_dir, slice_paths = await pwsh_splitfile(local_path, slice_size)
    assert len(slice_paths) == slices

    try:
        for i, slice_path in enumerate(slice_paths):
            slice_md5 = await pwsh_md5(slice_path)
            assert await upload_slice(
                base_url=base_url,
                preupload_id=preupload_id,
                slice_no=i + 1,
                slice_md5=slice_md5,
                slice_path=slice_path,
            )
    finally:
        await pwsh_rmdir(tmp_dir)

    for _ in range(60):
        fileID = await verify_complete(preupload_id)
        if fileID != -1:
            return fileID
        await asyncio.sleep(1)

    return -1


if __name__ == "__main__":
    from asyncio import run
    from argparse import ArgumentParser

    parser = ArgumentParser(description="上传文件到Pan")
    parser.add_argument("local_path", help="本地文件路径")
    parser.add_argument("remote_path", help="远程文件路径")
    args = parser.parse_args()

    print("Uploaded FileID:", run(upload(args.local_path, args.remote_path)))
