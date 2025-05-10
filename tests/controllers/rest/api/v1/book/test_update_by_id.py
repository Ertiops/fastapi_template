from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import BookTable
from tests.utils import now_utc


def api_url(book_id: UUID = uuid4()) -> str:
    return f"/api/v1/books/{book_id}/"


@pytest.mark.parametrize(
    "json_data",
    (
        dict(title="t" * 2),
        dict(title="t" * 256),
        dict(year=-1),
        dict(year=now_utc().year + 1),
        dict(author="t" * 2),
        dict(author="t" * 256),
    ),
)
async def test__update_by_id__unprocessable_entity(
    client: AsyncClient, json_data: Mapping[str, Any]
) -> None:
    response = await client.patch(api_url(), json=json_data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__update_by_id__unprocessable_entity__empty_payload(
    client: AsyncClient,
) -> None:
    response = await client.patch(api_url())
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__update_by_id__not_found(client: AsyncClient) -> None:
    response = await client.patch(
        api_url(),
        json=dict(title="test_book"),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test__update_by_id__ok__status(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    response = await client.patch(
        api_url(db_book.id),
        json=dict(title="test_book"),
    )
    assert response.status_code == HTTPStatus.OK


async def test__update_by_id__ok__format(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    json_data = dict(
        title="test_title",
        year=now_utc().year,
        author="test_author",
    )
    response = await client.patch(api_url(db_book.id), json=json_data)
    assert response.json() == dict(
        id=str(db_book.id),
        title=json_data.get("title"),
        author=json_data.get("author"),
        year=json_data.get("year"),
        created_at=IsStr,
        updated_at=IsStr,
    )


async def test__update_by_id__conflict__duplicate(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book(year=now_utc().year)
    db_book_to_update: BookTable = await create_book()
    response = await client.patch(
        api_url(db_book_to_update.id),
        json=dict(
            title=db_book.title,
            year=db_book.year,
            author=db_book.author,
        ),
    )
    assert response.status_code == HTTPStatus.CONFLICT
