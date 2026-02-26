__all__ = [
    "MkdirData",
    "CreateFileData",
    "UploadCompleteData",
    "RenameSuccessData",
    "RenameFailData",
    "RenameData",
    "CopyData",
    "CopyAsyncData",
    "CopyProgressData",
    "RecoverData",
    "FileBasicInfo",
    "FileInfo",
    "FileInfosData",
    "FileListData",
    "DownloadData",
]

from datetime import datetime

from pydantic import BaseModel

from ..models import BaseData
from .enums import FileCategoryEnum, CopyProgressEnum


class MkdirData(BaseData):
    dirID: int


class CreateFileData(BaseData):
    fileID: int
    preuploadID: str
    reuse: bool
    sliceSize: int
    servers: list[str]


class UploadCompleteData(BaseData):
    completed: bool
    fileID: int


class RenameSuccessData(BaseData):
    fileID: int
    updateAt: datetime


class RenameFailData(BaseData):
    fileID: int
    message: str


class RenameData(BaseData):
    successList: list[RenameSuccessData]
    failList: list[RenameFailData]


class CopyData(BaseData):
    sourceFileId: int
    targetFileId: int


class CopyAsyncData(BaseData):
    taskId: int


class CopyProgressData(BaseData):
    taskId: int
    status: CopyProgressEnum


class RecoverData(BaseData):
    abnormalFileIDs: list[int]


class FileBasicInfo(BaseModel):
    fileId: int
    filename: str
    parentFileId: int
    type: bool
    etag: str
    size: int
    category: FileCategoryEnum
    status: int
    trashed: bool


class FileInfo(FileBasicInfo):
    punishFlag: int
    s3KeyFlag: str
    storageNode: str
    createAt: datetime
    updateAt: datetime


class FileInfosData(BaseData):
    fileList: list[FileInfo]


class FileListData(BaseData):
    lastFileId: int
    fileList: list[FileBasicInfo]


class DownloadData(BaseData):
    downloadUrl: str
