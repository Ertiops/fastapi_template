from collections.abc import Callable, Mapping
from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import BookTable

API_URL = "/api/v1/books/"


@pytest.mark.parametrize(
    "params",
    [
        dict(limit=-1),
        dict(limit=0),
        dict(limit="a"),
        dict(offset=-1),
        dict(offset="a"),
        dict(limit=101),
    ],
)
async def test__get_list__unprocessable_entity(
    client: AsyncClient, params: Mapping[str, Any]
) -> None:
    response = await client.get(API_URL, params=params)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test__get_list__ok__status(client: AsyncClient) -> None:
    response = await client.get(API_URL)
    assert response.status_code == HTTPStatus.OK


async def test__get_list__ok__format(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    response = await client.get(API_URL)
    assert response.json() == dict(
        total=len(db_books),
        items=[
            dict(
                id=str(db_book.id),
                title=db_book.title,
                author=db_book.author,
                year=db_book.year,
                created_at=IsStr,
                updated_at=IsStr,
            )
            for db_book in db_books
        ],
    )


async def test__get_list__validate_limit(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    response = await client.get(API_URL, params=dict(limit=1))
    assert response.json() == dict(
        total=len(db_books),
        items=[
            dict(
                id=str(db_book.id),
                title=db_book.title,
                author=db_book.author,
                year=db_book.year,
                created_at=IsStr,
                updated_at=IsStr,
            )
            for db_book in db_books
        ][:1],
    )


async def test__get_list__validate_offset(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    response = await client.get(API_URL, params=dict(offset=1))
    assert response.json() == dict(
        total=len(db_books),
        items=[
            dict(
                id=str(db_book.id),
                title=db_book.title,
                author=db_book.author,
                year=db_book.year,
                created_at=IsStr,
                updated_at=IsStr,
            )
            for db_book in db_books
        ][1:],
    )


async def test__get_list__empty_list(client: AsyncClient) -> None:
    response = await client.get(API_URL)
    assert response.json() == dict(
        total=0,
        items=[],
    )
