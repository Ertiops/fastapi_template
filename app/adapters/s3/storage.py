import logging
import mimetypes
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from app.adapters.s3.client import S3Client
from app.application.exceptions import S3ClientException, ServiceUnavailableException
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
    UploadFileByKey,
    UploadFileToStorage,
)
from app.domain.interfaces.storages.file import IFileStorage

log = logging.getLogger(__name__)


class S3Storage(IFileStorage):
    __s3_client: S3Client

    def __init__(self, *, s3_client: S3Client) -> None:
        self.__s3_client = s3_client

    async def upload_file(self, *, input_dto: UploadFileToStorage, user: S3User) -> str:
        file_ext = self._detect_extension(input_dto=input_dto)
        key = self.__s3_client.build_file_key(
            input_dto=BuildFileKey(
                entity=input_dto.entity,
                file_id=uuid4(),
                file_ext=file_ext,
            ),
            user=user,
        )

        try:
            await self.__s3_client.upload_file(
                input_dto=UploadFileByKey(
                    key=key,
                    file=input_dto.file,
                    content_type=input_dto.content_type,
                    public_read=input_dto.public_read,
                    metadata=input_dto.metadata,
                ),
                user=user,
            )
            return self.__s3_client.get_external_url(
                input_dto=GetFileFromStorage(key=key),
                user=user,
            )
        except S3ClientException as exc:
            log.error("Failed to upload file to S3: %s", exc)
            raise ServiceUnavailableException(
                message="S3 is unavailable: failed to upload file."
            ) from exc

    async def get_file(self, *, input_dto: GetFileFromStorage, user: S3User) -> BytesIO:
        relative_key = self.__s3_client.convert_to_relative_key(
            input_dto=ConvertToRelativeKey(key=input_dto.key),
            user=user,
        )
        try:
            response = await self.__s3_client.get_file(
                input_dto=GetFileFromStorage(key=relative_key),
                user=user,
            )
            return BytesIO(await response["Body"].read())
        except S3ClientException as exc:
            log.error("Failed to get file from S3: %s", exc)
            raise ServiceUnavailableException(
                message="S3 is unavailable: failed to get file."
            ) from exc

    async def get_files(
        self,
        *,
        input_dto: GetFilesFromStorage,
        user: S3User,
    ) -> Sequence[BytesIO]:
        rel_keys = [
            self.__s3_client.convert_to_relative_key(
                input_dto=ConvertToRelativeKey(key=key),
                user=user,
            )
            for key in input_dto.keys
        ]
        out: list[BytesIO] = []
        try:
            for key in rel_keys:
                response = await self.__s3_client.get_file(
                    input_dto=GetFileFromStorage(key=key),
                    user=user,
                )
                body = response["Body"]
                async with body:
                    data = await body.read()
                out.append(BytesIO(data))
            return out
        except S3ClientException as exc:
            log.error("Failed to get files from S3: %s", exc)
            raise ServiceUnavailableException(
                message="S3 is unavailable: failed to get files."
            ) from exc

    async def remove_file(
        self,
        *,
        input_dto: RemoveFileFromStorage,
        user: S3User,
    ) -> None:
        relative_key = self.__s3_client.convert_to_relative_key(
            input_dto=ConvertToRelativeKey(key=input_dto.key),
            user=user,
        )
        try:
            await self.__s3_client.remove_file(
                input_dto=RemoveFileFromStorage(key=relative_key),
                user=user,
            )
        except S3ClientException as exc:
            log.error("Failed to remove file from S3: %s", exc)
            raise ServiceUnavailableException(
                message="S3 is unavailable: failed to remove file."
            ) from exc

    async def get_file_info(
        self,
        *,
        input_dto: GetFileInfoFromStorage,
        user: S3User,
    ) -> FileInfo:
        relative_key = self.__s3_client.convert_to_relative_key(
            input_dto=ConvertToRelativeKey(key=input_dto.key),
            user=user,
        )
        try:
            response = await self.__s3_client.get_file_info(
                input_dto=GetFileInfoFromStorage(key=relative_key),
                user=user,
            )
            return FileInfo(
                key=relative_key,
                size=response["ContentLength"],
                content_type=response.get("ContentType"),
                metadata=response.get("Metadata", {}),
                last_modified=response.get("LastModified"),
            )
        except S3ClientException as exc:
            log.error("Failed to get file info from S3: %s", exc)
            raise ServiceUnavailableException(
                message="S3 is unavailable: failed to get file info."
            ) from exc

    def get_file_url(self, *, input_dto: BuildFileUrl, user: S3User) -> str:
        key = self.__s3_client.build_file_key(
            input_dto=BuildFileKey(
                entity=input_dto.entity,
                file_id=input_dto.file_id,
                file_ext=input_dto.file_ext,
            ),
            user=user,
        )
        return self.__s3_client.get_external_url(
            input_dto=GetFileFromStorage(key=key),
            user=user,
        )

    def build_file_key(self, *, input_dto: BuildFileKey, user: S3User) -> str:
        return self.__s3_client.build_file_key(input_dto=input_dto, user=user)

    def convert_to_relative_key(
        self,
        *,
        input_dto: ConvertToRelativeKey,
        user: S3User,
    ) -> str:
        return self.__s3_client.convert_to_relative_key(input_dto=input_dto, user=user)

    def _detect_extension(self, *, input_dto: UploadFileToStorage) -> str:
        if input_dto.filename is not None:
            suffix = Path(input_dto.filename).suffix.lower().lstrip(".")
            if suffix:
                return suffix

        guessed = mimetypes.guess_extension(input_dto.content_type)
        if guessed is not None:
            normalized = guessed.lower().lstrip(".")
            if normalized:
                return normalized

        return "bin"
