from collections.abc import AsyncGenerator, AsyncIterator
from os import getenv

import aioboto3
import pytest
from botocore.config import Config
from botocore.exceptions import ClientError

from app.adapters.s3.client import S3ApiClient, S3Client
from app.adapters.s3.config import S3Config
from app.adapters.s3.storage import S3Storage
from app.domain.interfaces.storages.file import IFileStorage
from tests.utils.worker import get_worker_name


def _worker_bucket_name() -> str:
    base_bucket = getenv("APP_S3_BUCKET", "app")
    worker = get_worker_name()
    return f"{base_bucket}-{worker}" if worker != "master" else base_bucket


@pytest.fixture(scope="session")
def s3_config() -> S3Config:
    return S3Config(
        access_key=getenv("APP_S3_ACCESS_KEY", "secret"),
        secret_key=getenv("APP_S3_SECRET_KEY", "secretsecret"),
        bucket=_worker_bucket_name(),
        endpoint_url=getenv("APP_S3_ENDPOINT_URL", "http://127.0.0.1:9000"),
        max_pool_connections=int(getenv("APP_S3_MAX_POOL_CONNECTIONS", 10)),
        max_attempts=int(getenv("APP_S3_MAX_ATTEMPTS", 5)),
    )


@pytest.fixture(scope="session")
def s3_session() -> aioboto3.Session:
    return aioboto3.Session()


@pytest.fixture(scope="session")
async def s3_api_client(
    s3_config: S3Config,
    s3_session: aioboto3.Session,
) -> AsyncGenerator[S3ApiClient, None]:
    config = Config(
        max_pool_connections=s3_config.max_pool_connections,
        retries={"max_attempts": s3_config.max_attempts, "mode": "standard"},
    )
    async with s3_session.client(
        "s3",
        aws_secret_access_key=s3_config.secret_key,
        aws_access_key_id=s3_config.access_key,
        endpoint_url=s3_config.endpoint_url,
        config=config,
    ) as client:
        try:
            await client.create_bucket(Bucket=s3_config.bucket)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise
        yield client


@pytest.fixture
async def clear_bucket(
    s3_api_client: S3ApiClient,
    s3_config: S3Config,
) -> AsyncIterator[None]:
    yield
    response = await s3_api_client.list_objects_v2(Bucket=s3_config.bucket)
    contents = response.get("Contents", [])
    if not contents:
        return

    await s3_api_client.delete_objects(
        Bucket=s3_config.bucket,
        Delete={"Objects": [{"Key": obj["Key"]} for obj in contents]},
    )


@pytest.fixture
def s3_client(
    clear_bucket: None, s3_api_client: S3ApiClient, s3_config: S3Config
) -> S3Client:
    return S3Client(
        client=s3_api_client,
        bucket=s3_config.bucket,
        endpoint_url=s3_config.endpoint_url,
    )


@pytest.fixture
def s3_storage(s3_client: S3Client) -> IFileStorage:
    return S3Storage(s3_client=s3_client)
