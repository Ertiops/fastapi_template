from os import getenv

import pytest

from app.adapters.database.config import DatabaseConfig
from app.adapters.s3.config import S3Config
from app.application.config import AppConfig, SecretConfig
from app.presenters.rest.config import RestConfig
from tests.utils.worker import get_worker_name


def _worker_bucket_name() -> str:
    base_bucket = getenv("APP_S3_BUCKET", "app")
    worker = get_worker_name()
    return f"{base_bucket}-{worker}" if worker != "master" else base_bucket


@pytest.fixture(scope="session")
def rest_config(db_config: DatabaseConfig) -> RestConfig:
    return RestConfig(
        host=getenv("APP_REST_HOST", "127.0.0.1"),
        port=int(getenv("APP_REST_PORT", 8000)),
        app=AppConfig(debug=True),
        database=db_config,
        s3=S3Config(
            access_key=getenv("APP_S3_ACCESS_KEY", "secret"),
            secret_key=getenv("APP_S3_SECRET_KEY", "secret123"),
            bucket=_worker_bucket_name(),
            endpoint_url=getenv("APP_S3_ENDPOINT_URL", "http://127.0.0.1:9000"),
            max_pool_connections=int(getenv("APP_S3_MAX_POOL_CONNECTIONS", 10)),
            max_attempts=int(getenv("APP_S3_MAX_ATTEMPTS", 5)),
            multipart_chunk_size=int(getenv("APP_S3_MULTIPART_CHUNK_SIZE", 5242880)),
        ),
        secret=SecretConfig(),
    )
