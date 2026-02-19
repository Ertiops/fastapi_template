from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, BinaryIO
from uuid import UUID


@dataclass(frozen=True, kw_only=True, slots=True)
class S3User:
    id: UUID | None


@dataclass(frozen=True, kw_only=True, slots=True)
class UploadFileToStorage:
    entity: str
    file: BinaryIO
    content_type: str
    filename: str | None
    public_read: bool
    metadata: dict[str, Any] | None


@dataclass(frozen=True, kw_only=True, slots=True)
class UploadFileResult:
    file_url: str


@dataclass(frozen=True, kw_only=True, slots=True)
class UploadFileByKey:
    key: str
    file: BinaryIO
    content_type: str
    public_read: bool
    metadata: dict[str, Any] | None


@dataclass(frozen=True, kw_only=True, slots=True)
class GetFileFromStorage:
    key: str


@dataclass(frozen=True, kw_only=True, slots=True)
class GetFilesFromStorage:
    keys: Sequence[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class RemoveFileFromStorage:
    key: str


@dataclass(frozen=True, kw_only=True, slots=True)
class GetFileInfoFromStorage:
    key: str


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
class ConvertToRelativeKey:
    key: str


@dataclass(frozen=True, kw_only=True, slots=True)
class FileInfo:
    key: str
    size: int
    content_type: str | None
    metadata: dict[str, Any]
    last_modified: datetime | None
