from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import BookTable
from tests.utils import now_utc

API_URL = "/api/v1/books/"


@pytest.mark.parametrize(
    "json_data",
    (
        dict(title="t" * 2),
        dict(title="t" * 256),
        dict(year=0),
        dict(year=now_utc().year + 1),
        dict(author="t" * 2),
        dict(author="t" * 256),
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
            title="test_book",
            author="test_author",
            year=now_utc().year,
        ),
    )
    assert response.status_code == HTTPStatus.CREATED


async def test__create__ok__format(client: AsyncClient) -> None:
    response = await client.post(
        API_URL,
        json=dict(
            title="test_book",
            author="test_author",
            year=now_utc().year,
        ),
    )
    assert response.json() == dict(
        id=IsStr,
        title="test_book",
        author="test_author",
        year=now_utc().year,
        created_at=IsStr,
        updated_at=IsStr,
    )


async def test__create__duplicate__conflict(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book(year=now_utc().year)
    response = await client.post(
        API_URL,
        json=dict(
            title=db_book.title,
            year=db_book.year,
            author=db_book.author,
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT
