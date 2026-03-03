from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, unique
from typing import Any, BinaryIO
from uuid import UUID

from yarl import URL


@unique
class FileEntity(StrEnum):
    USERS = "users"
    MOVIES = "movies"


@unique
class FileExtension(StrEnum):
    PDF = "pdf"
    MP4 = "mp4"
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    WEBP = "webp"
    MP3 = "mp3"
    MOV = "mov"
    HEVC = "hevc"
    M4V = "m4v"
    HEIF = "heif"
    HEIC = "heic"
    H265 = "h265"


@unique
class FileType(StrEnum):
    PDF = "application/pdf"
    MP4 = "video/mp4"
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    WEBP = "image/webp"
    MP3 = "audio/mp3"
    QUICKTIME = "video/quicktime"
    HEVC = "video/hevc"
    M4V = "video/x-m4v"
    HEIF = "image/heif"
    HEIC = "image/heic"
    H265 = "video/h265"
    OCTET_STREAM = "application/octet-stream"


FILE_CONNTENT_EXTENSION_MAPPING: Mapping[FileType, FileExtension] = {
    FileType.PDF: FileExtension.PDF,
    FileType.MP4: FileExtension.MP4,
    FileType.PNG: FileExtension.PNG,
    FileType.JPEG: FileExtension.JPEG,
    FileType.JPG: FileExtension.JPG,
    FileType.WEBP: FileExtension.WEBP,
    FileType.MP3: FileExtension.MP3,
    FileType.QUICKTIME: FileExtension.MOV,
    FileType.HEVC: FileExtension.HEVC,
    FileType.M4V: FileExtension.M4V,
    FileType.HEIF: FileExtension.HEIF,
    FileType.HEIC: FileExtension.HEIC,
    FileType.H265: FileExtension.H265,
}


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateFile:
    entity: FileEntity
    file: BinaryIO
    content_type: FileType
    filename: str
    public_read: bool
    metadata: dict[str, Any]


@dataclass(frozen=True, kw_only=True, slots=True)
class File:
    url: URL


@dataclass(frozen=True, kw_only=True, slots=True)
class UploadFileByKey:
    key: str
    file: BinaryIO
    content_type: str
    public_read: bool
    metadata: dict[str, Any] | None


@dataclass(frozen=True, kw_only=True, slots=True)
class GetFileList:
    keys: Sequence[str | URL]


@dataclass(frozen=True, kw_only=True, slots=True)
class BuildFileUrl:
    entity: str
    file_id: UUID
    file_ext: str


@dataclass(frozen=True, kw_only=True, slots=True)
class BuildFileKey:
    entity: str
    file_id: UUID
    file_ext: str


@dataclass(frozen=True, kw_only=True, slots=True)
class FileInfo:
    key: str
    size: int
    content_type: str | None
    metadata: dict[str, Any]
    last_modified: datetime | None
