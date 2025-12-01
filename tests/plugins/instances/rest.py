from collections.abc import AsyncGenerator
from typing import Any

import pytest
from aiomisc.service.uvicorn import UvicornApplication
from httpx import URL, ASGITransport, AsyncClient

from app.presenters.rest.config import RestConfig
from app.presenters.rest.service import RestService


@pytest.fixture(scope="session")
def rest_base_url() -> URL:
    return URL(scheme="http", host="127.0.0.1", port=8000)


@pytest.fixture(scope="session")
async def test_app(rest_config: RestConfig, rest_base_url: URL) -> UvicornApplication:
    service = RestService(
        host=rest_base_url.host,
        port=rest_base_url.port,
        config=rest_config,
    )
    return await service.create_application()


@pytest.fixture(scope="session")
async def client(
    test_app: UvicornApplication, rest_base_url: URL
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url=rest_base_url
    ) as client:
        yield client
