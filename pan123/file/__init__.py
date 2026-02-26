from types import NoneType
from hashlib import md5
from random import choice
from asyncio import sleep

from ..core import Client
from ..exception import ClientException
from ..log import logger
from . import models, enums

__all__ = [
    "enums",
    "models",
    "File",
]


class File:
    def __init__(self, client: Client):
        self._client: Client = client

    async def mkdir(self, name: str, parent_id: int = 0) -> models.MkdirData:
        return await self._client.request(
            method="POST",
            endpoint="/upload/v1/file/mkdir",
            model=models.MkdirData,
            json={
                "name": name,
                "parentID": parent_id,
            },
        )

    async def _create_file(
        self,
        parent_id: int,
        name: str,
        md5: str,
        size: int,
        do_cover: bool = False,
        contain_dir: bool = False,
    ) -> models.CreateFileData:
        return await self._client.request(
            method="POST",
            endpoint="/upload/v2/file/create",
            model=models.CreateFileData,
            json={
                "parentFileID": parent_id,
                "filename": name,
                "etag": md5,
                "size": size,
                "duplicate": int(do_cover) + 1,
                "containDir": contain_dir,
            },
        )

    async def _upload_slice(
        self,
        base_url: str,
        preupload_id: str,
        slice_no: int,
        slice_data: bytes,
    ) -> None:
        return await self._client.request(
            method="POST",
            base_url=base_url,
            endpoint=f"/upload/v2/file/slice",
            model=NoneType,
            data={
                "preuploadID": preupload_id,
                "sliceNo": slice_no,
                "sliceMD5": md5(slice_data).hexdigest(),
            },
            files={"slice": slice_data},
        )

    async def _upload_complete(
        self,
        preupload_id: str,
    ) -> models.UploadCompleteData:
        return await self._client.request(
            method="POST",
            endpoint="/upload/v2/file/upload_complete",
            model=models.UploadCompleteData,
            json={
                "preuploadID": preupload_id,
            },
        )

    async def upload(
        self,
        local_path: str,
        remote_path: str,
        parent_id: int = 0,
        do_cover: bool = False,
    ) -> int:
        with open(local_path, "rb") as f:
            file_data = f.read()
        file_size = len(file_data)
        remote_file = await self._create_file(
            parent_id=parent_id,
            name=remote_path,
            md5=md5(file_data).hexdigest(),
            size=file_size,
            do_cover=do_cover,
            contain_dir="/" in remote_path,
        )
        if remote_file.reuse:
            return remote_file.fileID
        for idx, start in enumerate(range(0, file_size, remote_file.sliceSize), 1):
            end = min(start + remote_file.sliceSize, file_size)
            slice = file_data[start:end]
            await self._upload_slice(
                base_url=choice(remote_file.servers),
                preupload_id=remote_file.preuploadID,
                slice_no=idx,
                slice_data=slice,
            )
        while True:
            try:
                complete = await self._upload_complete(
                    preupload_id=remote_file.preuploadID,
                )
            except ClientException[models.UploadCompleteData] as e:
                logger.error(e)
                complete = e.response.data
            if complete and complete.completed:
                return complete.fileID
            await sleep(1)

    async def rename(self, files: dict[int, str]) -> models.RenameData:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/rename",
            model=models.RenameData,
            json={
                "renameList": [f"{idx}|{name}" for idx, name in files.items()],
            },
        )

    async def trash(self, file_ids: list[int]) -> None:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/trash",
            model=NoneType,
            json={
                "fileIDs": file_ids,
            },
        )

    async def copy(self, file_id: int, target_dir_id: int) -> models.CopyData:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/copy",
            model=models.CopyData,
            json={
                "fileId": file_id,
                "targetDirId": target_dir_id,
            },
        )

    async def copy_async(
        self, file_ids: list[int], target_dir_id: int
    ) -> models.CopyAsyncData:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/async/copy",
            model=models.CopyAsyncData,
            json={
                "fileIds": file_ids,
                "targetDirId": target_dir_id,
            },
        )

    async def copy_progress(self, task_id: int) -> models.CopyProgressData:
        return await self._client.request(
            method="GET",
            endpoint="/api/v1/file/async/copy/process",
            model=models.CopyProgressData,
            params={
                "taskId": task_id,
            },
        )

    async def recover(self, file_ids: list[int]) -> models.RecoverData:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/recover",
            model=models.RecoverData,
            json={
                "fileIDs": file_ids,
            },
        )

    async def recover_by_path(self, file_ids: list[int], target_dir_id: int) -> None:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/recover/by_path",
            model=NoneType,
            json={
                "fileIDs": file_ids,
                "parentFileID": target_dir_id,
            },
        )

    async def infos(self, file_ids: list[int]) -> models.FileInfosData:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/infos",
            model=models.FileInfosData,
            json={
                "fileIds": file_ids,
            },
        )

    async def search(
        self,
        dir_id: int = 0,
        limit: int = 100,
        search_data: str | None = None,
        precised_search: bool | None = None,
        first_id: int | None = None,
    ) -> models.FileListData:
        return await self._client.request(
            method="GET",
            endpoint="/api/v2/file/list",
            model=models.FileListData,
            params={
                "parentFileId": dir_id,
                "limit": limit,
                "searchData": search_data,
                "searchMode": (
                    int(precised_search) if precised_search is not None else None
                ),
                "lastFileId": first_id,
            },
        )

    async def move(self, file_ids: list[int], target_dir_id: int) -> None:
        return await self._client.request(
            method="POST",
            endpoint="/api/v1/file/move",
            model=NoneType,
            json={
                "fileIDs": file_ids,
                "toParentFileID": target_dir_id,
            },
        )

    async def download_info(self, file_id: int) -> models.DownloadData:
        return await self._client.request(
            method="GET",
            endpoint="/api/v1/file/download_info",
            model=models.DownloadData,
            params={
                "fileID": file_id,
            },
        )

    async def download(self, file_id: int, local_path: str) -> None:
        download_info = await self.download_info(file_id)
        logger.info(f"Downloading {download_info.downloadUrl} to {local_path}")
        async with self._client.get_client().stream(
            method="GET", url=download_info.downloadUrl, follow_redirects=True
        ) as resp:
            _ = resp.raise_for_status()
            with open(local_path, "wb") as f:
                async for chunk in resp.aiter_bytes():
                    _ = f.write(chunk)
        logger.info(f"Downloaded {download_info.downloadUrl} to {local_path}")
