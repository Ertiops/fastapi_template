from http import HTTPStatus

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

API_URL = "/api/v1/files/upload/"
pytestmark = pytest.mark.usefixtures("s3_api_client")


async def test__upload_file__ok__status(client: AsyncClient) -> None:
    response = await client.post(
        API_URL,
        data={"entity": "avatars"},
        files={"file": ("avatar.png", b"image", "image/png")},
    )
    assert response.status_code == HTTPStatus.OK


async def test__upload_file__ok__format(client: AsyncClient) -> None:
    response = await client.post(
        API_URL,
        data={"entity": "avatars"},
        files={"file": ("avatar.png", b"image", "image/png")},
    )
    assert response.json() == {"file_url": IsStr}
