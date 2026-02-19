from dataclasses import dataclass, field
from os import environ

from app.adapters.database.config import DatabaseConfig
from app.adapters.s3.config import S3Config
from app.application.config import AppConfig, SecretConfig


@dataclass
class RestConfig:
    host: str = field(default_factory=lambda: environ.get("APP_REST_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(environ.get("APP_REST_PORT", 8000)))

    app: AppConfig = field(default_factory=lambda: AppConfig())
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig())
    s3: S3Config = field(default_factory=lambda: S3Config())
    secret: SecretConfig = field(default_factory=lambda: SecretConfig())
