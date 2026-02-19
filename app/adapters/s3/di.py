from collections.abc import AsyncGenerator

from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from botocore.config import Config
from dishka import BaseScope, Component, Provider, Scope, provide

from app.adapters.s3.client import S3Client
from app.adapters.s3.config import S3Config
from app.adapters.s3.storage import S3Storage
from app.adapters.s3.utils import create_session
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
        self.multipart_chunk_size = config.multipart_chunk_size
        super().__init__(scope=scope, component=component)

    @provide(scope=Scope.APP)
    def session(self) -> AioSession:
        return create_session()

    @provide(scope=Scope.REQUEST)
    async def client(self, session: AioSession) -> AsyncGenerator[AioBaseClient, None]:
        config = Config(
            max_pool_connections=self.max_pool_connections,
            retries={"max_attempts": self.max_attempts, "mode": "standard"},
        )

        async with session.create_client(  # type: ignore[call-overload]
            "s3",
            aws_secret_access_key=self.secret_key,
            aws_access_key_id=self.access_key,
            endpoint_url=self.endpoint_url,
            config=config,
        ) as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def s3_client(self, client: AioBaseClient) -> S3Client:
        return S3Client(
            client=client,
            bucket=self.bucket,
            endpoint_url=self.endpoint_url,
            multipart_chunk_size=self.multipart_chunk_size,
        )

    @provide(scope=Scope.REQUEST)
    def s3_storage(self, s3_client: S3Client) -> IFileStorage:
        return S3Storage(s3_client=s3_client)
