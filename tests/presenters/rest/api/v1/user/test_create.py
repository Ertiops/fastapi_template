from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import UserTable

API_URL = "/api/v1/users/"


@pytest.mark.parametrize(
    "json_data",
    (
        dict(
            username="test_username",
        ),
        dict(email="test@test.com"),
        dict(
            username="test_username",
            email="testtest.com",
        ),
        dict(
            username="t" * 2,
            email="test@test.com",
        ),
        dict(
            username="t" * 256,
            email="test@test.com",
        ),
        dict(
            username="test_username",
            email="t" * 256 + "est@test.com",
        ),
    ),
)
async def test__create__unprocessable_entity(
    client: AsyncClient,
    json_data: Mapping[str, Any],
) -> None:
    response = await client.post(API_URL, json=json_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__create__ok__status(client: AsyncClient) -> None:
    response = await client.post(
        API_URL,
        json=dict(
            username="test_username",
            email="test@test.com",
        ),
    )
    assert response.status_code == HTTPStatus.CREATED


async def test__create__ok__format(client: AsyncClient) -> None:
    json_data = dict(
        username="test_username",
        email="test@test.com",
    )
    response = await client.post(
        API_URL,
        json=json_data,
    )
    assert response.json() == dict(
        id=IsStr,
        username=json_data.get("username"),
        email=json_data.get("email"),
        created_at=IsStr,
        updated_at=IsStr,
    )


async def test_create_user__conflict__duplicate__email(
    client: AsyncClient,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user(email="email@example.com")
    response = await client.post(
        API_URL,
        json=dict(
            username="username2",
            email=db_user.email,
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT


async def test_create_user__conflict__duplicate__username(
    client: AsyncClient,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user(username="test_username")
    response = await client.post(
        API_URL,
        json=dict(
            username=db_user.username,
            email="test@test.com",
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT
