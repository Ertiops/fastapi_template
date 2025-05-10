from collections.abc import Callable
from http import HTTPStatus
from uuid import UUID, uuid4

from dirty_equals import IsStr
from httpx import AsyncClient

from app.adapters.database.tables import BookTable


def api_url(book_id: UUID = uuid4()) -> str:
    return f"/api/v1/books/{book_id}/"


async def test__get_by_id__not_found__status(client: AsyncClient) -> None:
    response = await client.get(api_url())
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test__get_by_id__ok__status(
    create_book: Callable,
    client: AsyncClient,
) -> None:
    db_book: BookTable = await create_book()
    response = await client.get(api_url(db_book.id))
    assert response.status_code == HTTPStatus.OK


async def test__get_by_id__ok__format(create_book, client: AsyncClient) -> None:
    db_book: BookTable = await create_book()
    response = await client.get(api_url(db_book.id))
    assert response.json() == dict(
        id=str(db_book.id),
        title=db_book.title,
        year=db_book.year,
        author=db_book.author,
        created_at=IsStr,
        updated_at=IsStr,
    )
