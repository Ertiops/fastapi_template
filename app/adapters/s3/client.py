import logging
from typing import Any, Protocol

from botocore.exceptions import ClientError
from yarl import URL

from app.application.exceptions import S3ClientException
from app.domain.entities.file import (
    BuildFileKey,
    UploadFileByKey,
)

log = logging.getLogger(__name__)


class S3ApiClient(Protocol):
    async def create_bucket(self, **kwargs: Any) -> Any: ...
    async def put_object(self, **kwargs: Any) -> Any: ...
    async def get_object(self, **kwargs: Any) -> dict[str, Any]: ...
    async def delete_object(self, **kwargs: Any) -> Any: ...
    async def delete_objects(self, **kwargs: Any) -> Any: ...
    async def head_object(self, **kwargs: Any) -> dict[str, Any]: ...
    async def list_objects_v2(self, **kwargs: Any) -> dict[str, Any]: ...


class S3Client:
    __endpoint_url: URL
    __bucket: str
    __client: S3ApiClient

    def __init__(
        self,
        *,
        client: S3ApiClient,
        bucket: str,
        endpoint_url: str | URL,
    ) -> None:
        self.__client = client
        self.__endpoint_url = URL(str(endpoint_url).rstrip("/"))
        self.__bucket = bucket

    async def upload_file(self, *, input_dto: UploadFileByKey) -> None:
        extra_args: dict[str, Any] = {}
        if input_dto.public_read:
            extra_args["ACL"] = "public-read"

        extra_args["ContentType"] = input_dto.content_type
        extra_args["Metadata"] = input_dto.metadata or {}

        try:
            input_dto.file.seek(0)
            await self.__client.put_object(
                Bucket=self.__bucket,
                Key=input_dto.key,
                Body=input_dto.file.read(),
                **extra_args,
            )
        except ClientError as exc:
            log.error("Error uploading file %s to S3: %s", input_dto.key, exc)
            raise S3ClientException(message="Failed to upload file to S3.") from exc

    async def get_file(
        self,
        *,
        key: str,
    ) -> dict[str, Any]:
        try:
            return await self.__client.get_object(
                Bucket=self.__bucket,
                Key=key,
            )
        except ClientError as exc:
            log.error("Error getting file %s from S3: %s", key, exc)
            raise S3ClientException(message="Failed to get file from S3.") from exc

    async def remove_file(self, *, key: str) -> None:
        try:
            await self.__client.delete_object(
                Bucket=self.__bucket,
                Key=key,
            )
        except ClientError as exc:
            log.error("Error removing file %s from S3: %s", key, exc)
            raise S3ClientException(message="Failed to remove file from S3.") from exc

    async def get_file_info(self, *, key: str) -> dict[str, Any]:
        try:
            return await self.__client.head_object(
                Bucket=self.__bucket,
                Key=key,
            )
        except ClientError as exc:
            log.error("Error getting file info %s from S3: %s", key, exc)
            raise S3ClientException(message="Failed to get file info from S3.") from exc

    def get_external_url(self, *, key: str) -> URL:
        key = key.lstrip("/")
        return self.__endpoint_url.with_path(f"/{self.__bucket}/{key}")

    def build_file_key(self, *, input_dto: BuildFileKey) -> str:
        return f"{input_dto.entity}/{input_dto.file_id}.{input_dto.file_ext}"

    def convert_to_relative_key(self, *, key: str | URL) -> str:
        parsed = key if isinstance(key, URL) else URL(key)
        if parsed.scheme and parsed.host:
            path = parsed.path.lstrip("/")
            bucket_prefix = f"{self.__bucket}/"
            if path.startswith(bucket_prefix):
                return path[len(bucket_prefix) :]
            return path
        return str(key).lstrip("/")
