from collections.abc import Sequence
from io import BytesIO
from typing import Protocol

from app.domain.entities.file import (
    BuildFileKey,
    BuildFileUrl,
    ConvertToRelativeKey,
    FileInfo,
    GetFileFromStorage,
    GetFileInfoFromStorage,
    GetFilesFromStorage,
    RemoveFileFromStorage,
    S3User,
    UploadFileToStorage,
)


class IFileStorage(Protocol):
    async def upload_file(self, *, input_dto: UploadFileToStorage, user: S3User) -> str:
        pass

    async def get_file(self, *, input_dto: GetFileFromStorage, user: S3User) -> BytesIO:
        pass

    async def get_files(
        self, *, input_dto: GetFilesFromStorage, user: S3User
    ) -> Sequence[BytesIO]:
        pass

    async def remove_file(
        self,
        *,
        input_dto: RemoveFileFromStorage,
        user: S3User,
    ) -> None:
        pass

    async def get_file_info(
        self, *, input_dto: GetFileInfoFromStorage, user: S3User
    ) -> FileInfo:
        pass

    def get_file_url(self, *, input_dto: BuildFileUrl, user: S3User) -> str:
        pass

    def build_file_key(self, *, input_dto: BuildFileKey, user: S3User) -> str:
        pass

    def convert_to_relative_key(
        self,
        *,
        input_dto: ConvertToRelativeKey,
        user: S3User,
    ) -> str:
        pass
