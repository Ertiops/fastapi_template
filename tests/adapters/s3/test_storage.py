from io import BytesIO
from urllib.parse import urlparse
from uuid import uuid4

from aiobotocore.client import AioBaseClient

from app.adapters.s3.client import S3Client
from app.adapters.s3.storage import S3Storage
from app.domain.entities.file import (
    BuildFileKey,
    BuildFileUrl,
    ConvertToRelativeKey,
    GetFileFromStorage,
    GetFileInfoFromStorage,
    GetFilesFromStorage,
    RemoveFileFromStorage,
    S3User,
    UploadFileToStorage,
)


async def test__upload_file(
    s3_storage: S3Storage,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    file_url = await s3_storage.upload_file(
        input_dto=UploadFileToStorage(
            entity="avatars",
            file=BytesIO(b"image"),
            content_type="image/png",
            filename="avatar.png",
            public_read=True,
            metadata=None,
        ),
        user=S3User(id=None),
    )
    key = urlparse(file_url).path.lstrip("/").replace(f"{s3_config.bucket}/", "", 1)
    response = await s3_api_client.head_object(Bucket=s3_config.bucket, Key=key)  # type: ignore[attr-defined]
    assert response["ContentType"] == "image/png"


async def test__get_file(
    s3_storage: S3Storage,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    key = f"avatars/{uuid4()}.png"
    await s3_api_client.put_object(  # type: ignore[attr-defined]
        Bucket=s3_config.bucket,
        Key=key,
        Body=b"image",
        ContentType="image/png",
    )

    file = await s3_storage.get_file(
        input_dto=GetFileFromStorage(
            key=f"{s3_config.endpoint_url}/{s3_config.bucket}/{key}"
        ),
        user=S3User(id=None),
    )
    assert file.getvalue() == b"image"


async def test__get_files(
    s3_storage: S3Storage,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    key = f"avatars/{uuid4()}.png"
    await s3_api_client.put_object(  # type: ignore[attr-defined]
        Bucket=s3_config.bucket,
        Key=key,
        Body=b"image",
        ContentType="image/png",
    )

    files = await s3_storage.get_files(
        input_dto=GetFilesFromStorage(
            keys=[f"{s3_config.endpoint_url}/{s3_config.bucket}/{key}"]
        ),
        user=S3User(id=None),
    )
    assert files[0].getvalue() == b"image"


async def test__remove_file(
    s3_storage: S3Storage,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    key = f"avatars/{uuid4()}.png"
    await s3_api_client.put_object(  # type: ignore[attr-defined]
        Bucket=s3_config.bucket,
        Key=key,
        Body=b"image",
        ContentType="image/png",
    )

    await s3_storage.remove_file(
        input_dto=RemoveFileFromStorage(
            key=f"{s3_config.endpoint_url}/{s3_config.bucket}/{key}"
        ),
        user=S3User(id=None),
    )
    response = await s3_api_client.list_objects_v2(Bucket=s3_config.bucket)  # type: ignore[attr-defined]
    assert response.get("Contents", []) == []


async def test__get_file_info(
    s3_storage: S3Storage,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    key = f"avatars/{uuid4()}.png"
    await s3_api_client.put_object(  # type: ignore[attr-defined]
        Bucket=s3_config.bucket,
        Key=key,
        Body=b"image",
        ContentType="image/png",
    )

    info = await s3_storage.get_file_info(
        input_dto=GetFileInfoFromStorage(
            key=f"{s3_config.endpoint_url}/{s3_config.bucket}/{key}"
        ),
        user=S3User(id=None),
    )
    assert info.size == 5


def test__get_file_url(s3_storage: S3Storage) -> None:
    file_url = s3_storage.get_file_url(
        input_dto=BuildFileUrl(entity="avatars", file_id=uuid4(), file_ext="png"),
        user=S3User(id=None),
    )
    assert file_url.startswith("http")


def test__build_file_key(s3_storage: S3Storage) -> None:
    key = s3_storage.build_file_key(
        input_dto=BuildFileKey(entity="avatars", file_id=uuid4(), file_ext="png"),
        user=S3User(id=None),
    )
    assert key.startswith("avatars/")


def test__convert_to_relative_key(s3_storage: S3Storage, s3_config) -> None:
    key = s3_storage.convert_to_relative_key(
        input_dto=ConvertToRelativeKey(
            key=f"{s3_config.endpoint_url}/{s3_config.bucket}/avatars/{uuid4()}.png"
        ),
        user=S3User(id=None),
    )
    assert key.startswith("avatars/")


async def test__client_get_file(
    s3_client: S3Client,
    s3_api_client: AioBaseClient,
    s3_config,
) -> None:
    key = f"avatars/{uuid4()}.png"
    await s3_api_client.put_object(  # type: ignore[attr-defined]
        Bucket=s3_config.bucket,
        Key=key,
        Body=b"image",
    )
    response = await s3_client.get_file(
        input_dto=GetFileFromStorage(key=key),
        user=S3User(id=None),
    )
    body = await response["Body"].read()
    assert body == b"image"
