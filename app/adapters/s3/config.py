from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, slots=True, kw_only=True)
class S3Config:
    access_key: str = field(
        default_factory=lambda: environ.get("APP_S3_ACCESS_KEY", "secret")
    )
    secret_key: str = field(
        default_factory=lambda: environ.get("APP_S3_SECRET_KEY", "secret")
    )
    bucket: str = field(default_factory=lambda: environ.get("APP_S3_BUCKET", "app"))
    endpoint_url: str = field(
        default_factory=lambda: environ.get(
            "APP_S3_ENDPOINT_URL", "http://127.0.0.1:9000"
        )
    )
    max_pool_connections: int = field(
        default_factory=lambda: int(environ.get("APP_S3_MAX_POOL_CONNECTIONS", 10))
    )
    max_attempts: int = field(
        default_factory=lambda: int(environ.get("APP_S3_MAX_ATTEMPTS", 5))
    )
