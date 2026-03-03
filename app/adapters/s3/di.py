from collections.abc import AsyncGenerator

import aioboto3
from botocore.config import Config
from dishka import BaseScope, Component, Provider, Scope, provide

from app.adapters.s3.client import S3ApiClient, S3Client
from app.adapters.s3.config import S3Config
from app.adapters.s3.storage import S3Storage
from app.domain.interfaces.storages.file import IFileStorage


class S3Provider(Provider):
    def __init__(
        self,
        config: S3Config,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        self.access_key = config.access_key
        self.secret_key = config.secret_key
        self.bucket = config.bucket
        self.endpoint_url = config.endpoint_url
        self.max_pool_connections = config.max_pool_connections
        self.max_attempts = config.max_attempts
        super().__init__(scope=scope, component=component)

    @provide(scope=Scope.APP)
    def session(self) -> aioboto3.Session:
        return aioboto3.Session()

    @provide(scope=Scope.REQUEST)
    async def client(
        self, session: aioboto3.Session
    ) -> AsyncGenerator[S3ApiClient, None]:
        config = Config(
            max_pool_connections=self.max_pool_connections,
            retries=dict(max_attempts=self.max_attempts, mode="standard"),
        )

        async with session.client(
            "s3",
            aws_secret_access_key=self.secret_key,
            aws_access_key_id=self.access_key,
            endpoint_url=self.endpoint_url,
            config=config,
        ) as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def s3_client(self, client: S3ApiClient) -> S3Client:
        return S3Client(
            client=client,
            bucket=self.bucket,
            endpoint_url=self.endpoint_url,
        )

    @provide(scope=Scope.REQUEST)
    def s3_storage(self, s3_client: S3Client) -> IFileStorage:
        return S3Storage(s3_client=s3_client)
