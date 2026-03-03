from collections.abc import Sequence
from io import BytesIO
from typing import Protocol

from yarl import URL

from app.domain.entities.file import (
    BuildFileKey,
    BuildFileUrl,
    CreateFile,
    FileInfo,
    GetFileList,
)


class IFileStorage(Protocol):
    async def upload_file(self, *, input_dto: CreateFile) -> URL:
        pass

    async def get_file(self, *, key: str | URL) -> BytesIO:
        pass

    async def get_files(self, *, input_dto: GetFileList) -> Sequence[BytesIO]:
        pass

    async def remove_file(self, *, key: str | URL) -> None:
        pass

    async def get_file_info(self, *, key: str | URL) -> FileInfo:
        pass

    def get_file_url(self, *, input_dto: BuildFileUrl) -> URL:
        pass

    def build_file_key(self, *, input_dto: BuildFileKey) -> str:
        pass

    def convert_to_relative_key(self, *, key: str | URL) -> str:
        pass
