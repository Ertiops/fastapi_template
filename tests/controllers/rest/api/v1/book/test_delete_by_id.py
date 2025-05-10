from collections.abc import Callable
from http import HTTPStatus
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.tables import BookTable
from tests.utils import now_utc


def api_url(book_id: UUID = uuid4()) -> str:
    return f"/api/v1/books/{book_id}/"


async def test__delete_by_id__no_content__status(
    create_book: Callable, client: AsyncClient
) -> None:
    db_book: BookTable = await create_book()
    response = await client.delete(api_url(db_book.id))
    assert response.status_code == HTTPStatus.NO_CONTENT


async def test__delete_by_id__validate_deleted_at(
    client: AsyncClient,
    session: AsyncSession,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    await client.delete(api_url(db_book.id))
    await session.refresh(db_book)
    assert db_book.deleted_at is not None


async def test__delete_by_id__not_found(client: AsyncClient) -> None:
    response = await client.delete(api_url())
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test__delete_by_id__not_found__deleted(
    client: AsyncClient,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book(deleted_at=now_utc())
    response = await client.delete(api_url(db_book.id))
    assert response.status_code == HTTPStatus.NOT_FOUND
