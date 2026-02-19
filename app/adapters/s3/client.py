import logging
from typing import Any
from urllib.parse import urlparse

from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from app.application.exceptions import S3ClientException
from app.domain.entities.file import (
    BuildFileKey,
    ConvertToRelativeKey,
    GetFileFromStorage,
    GetFileInfoFromStorage,
    RemoveFileFromStorage,
    S3User,
    UploadFileByKey,
)

log = logging.getLogger(__name__)


class S3Client:
    _endpoint_url: str
    _bucket: str
    _client: AioBaseClient
    _multipart_chunk_size: int

    def __init__(
        self,
        *,
        client: AioBaseClient,
        bucket: str,
        endpoint_url: str,
        multipart_chunk_size: int,
    ) -> None:
        self._client = client
        self._endpoint_url = endpoint_url.rstrip("/")
        self._bucket = bucket
        self._multipart_chunk_size = multipart_chunk_size

    async def upload_file(self, *, input_dto: UploadFileByKey, user: S3User) -> None:
        upload_id: str | None = None
        parts: list[dict[str, Any]] = []
        part_number = 1

        extra_args: dict[str, Any] = {}
        if input_dto.public_read:
            extra_args["ACL"] = "public-read"

        extra_args["ContentType"] = input_dto.content_type
        extra_args["Metadata"] = input_dto.metadata or {}

        try:
            input_dto.file.seek(0)
            first_chunk = input_dto.file.read(self._multipart_chunk_size)
            if not first_chunk:
                await self._client.put_object(  # type: ignore[attr-defined]
                    Bucket=self._bucket,
                    Key=input_dto.key,
                    Body=b"",
                    **extra_args,
                )
                return

            create_resp = await self._client.create_multipart_upload(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=input_dto.key,
                **extra_args,
            )
            upload_id = create_resp["UploadId"]

            chunk: bytes = first_chunk
            while chunk:
                upload_part_resp = await self._client.upload_part(  # type: ignore[attr-defined]
                    Bucket=self._bucket,
                    Key=input_dto.key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append(
                    {
                        "PartNumber": part_number,
                        "ETag": upload_part_resp["ETag"],
                    }
                )
                part_number += 1
                chunk = input_dto.file.read(self._multipart_chunk_size)

            await self._client.complete_multipart_upload(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=input_dto.key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        except ClientError as exc:
            log.error("Error uploading file %s to S3: %s", input_dto.key, exc)
            if upload_id is not None:
                await self._abort_multipart_upload(
                    key=input_dto.key,
                    upload_id=upload_id,
                )
            raise S3ClientException(message="Failed to upload file to S3.") from exc

    async def get_file(
        self,
        *,
        input_dto: GetFileFromStorage,
        user: S3User,
    ) -> dict[str, Any]:
        try:
            return await self._client.get_object(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=input_dto.key,
            )
        except ClientError as exc:
            log.error("Error getting file %s from S3: %s", input_dto.key, exc)
            raise S3ClientException(message="Failed to get file from S3.") from exc

    async def remove_file(
        self,
        *,
        input_dto: RemoveFileFromStorage,
        user: S3User,
    ) -> None:
        try:
            await self._client.delete_object(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=input_dto.key,
            )
        except ClientError as exc:
            log.error("Error removing file %s from S3: %s", input_dto.key, exc)
            raise S3ClientException(message="Failed to remove file from S3.") from exc

    async def get_file_info(
        self,
        *,
        input_dto: GetFileInfoFromStorage,
        user: S3User,
    ) -> dict[str, Any]:
        try:
            return await self._client.head_object(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=input_dto.key,
            )
        except ClientError as exc:
            log.error("Error getting file info %s from S3: %s", input_dto.key, exc)
            raise S3ClientException(message="Failed to get file info from S3.") from exc

    def get_external_url(self, *, input_dto: GetFileFromStorage, user: S3User) -> str:
        return f"{self._endpoint_url}/{self._bucket}/{input_dto.key}"

    def build_file_key(self, *, input_dto: BuildFileKey, user: S3User) -> str:
        return f"{input_dto.entity}/{input_dto.file_id}.{input_dto.file_ext}"

    def convert_to_relative_key(
        self,
        *,
        input_dto: ConvertToRelativeKey,
        user: S3User,
    ) -> str:
        parsed = urlparse(input_dto.key)
        if parsed.scheme and parsed.netloc:
            path = parsed.path.lstrip("/")
            bucket_prefix = f"{self._bucket}/"
            if path.startswith(bucket_prefix):
                return path[len(bucket_prefix) :]
            return path
        return input_dto.key.lstrip("/")

    async def _abort_multipart_upload(self, *, key: str, upload_id: str) -> None:
        try:
            await self._client.abort_multipart_upload(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=key,
                UploadId=upload_id,
            )
        except ClientError as exc:
            log.error("Error aborting multipart upload for %s: %s", key, exc)
