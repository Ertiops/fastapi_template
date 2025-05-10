from collections.abc import Callable
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsDatetime, IsUUID

from app.adapters.database.storages.book import BookStorage
from app.adapters.database.tables import BookTable
from app.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domains.entities.book import (
    Book,
    BookListParams,
    CreateBook,
    UpdateBook,
)
from tests.utils import now_utc


async def test__create(book_storage: BookStorage) -> None:
    create_data = CreateBook(
        title="title",
        year=now_utc().year,
        author="author",
    )
    book = await book_storage.create(input_dto=create_data)
    assert book == Book(
        id=IsUUID,
        title=create_data.title,
        year=create_data.year,
        author=create_data.author,
        created_at=IsDatetime,
        updated_at=IsDatetime,
    )


async def test__create__entity_already_exists_exception(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    with pytest.raises(EntityAlreadyExistsException):
        await book_storage.create(
            input_dto=CreateBook(
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
            )
        )


async def test__get_by_id(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    book = await book_storage.get_by_id(input_id=db_book.id)
    assert book == Book(
        id=db_book.id,
        title=db_book.title,
        year=db_book.year,
        author=db_book.author,
        created_at=db_book.created_at,
        updated_at=db_book.updated_at,
    )


async def test__get_by_id__none(book_storage: BookStorage) -> None:
    assert await book_storage.get_by_id(input_id=uuid4()) is None


async def test_get_by_id__deleted(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book(deleted_at=now_utc())
    assert await book_storage.get_by_id(input_id=db_book.id) is None


async def test__get_list(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    books = await book_storage.get_list(input_dto=BookListParams(limit=10, offset=0))
    assert books == [
        Book(
            id=db_book.id,
            title=db_book.title,
            year=db_book.year,
            author=db_book.author,
            created_at=db_book.created_at,
            updated_at=db_book.updated_at,
        )
        for db_book in db_books
    ]


async def test__get_list__validate_limit(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    assert await book_storage.get_list(input_dto=BookListParams(limit=1, offset=0)) == [
        Book(
            id=db_books[0].id,
            title=db_books[0].title,
            year=db_books[0].year,
            author=db_books[0].author,
            created_at=db_books[0].created_at,
            updated_at=db_books[0].updated_at,
        )
    ]


async def test__get_list__validate_offset(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    assert await book_storage.get_list(input_dto=BookListParams(limit=2, offset=1)) == [
        Book(
            id=db_books[1].id,
            title=db_books[1].title,
            year=db_books[1].year,
            author=db_books[1].author,
            created_at=db_books[1].created_at,
            updated_at=db_books[1].updated_at,
        )
    ]


async def test__get_list__empty_list(
    book_storage: BookStorage,
) -> None:
    db_books = await book_storage.get_list(input_dto=BookListParams(limit=10, offset=0))
    assert db_books == []


async def test__count(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    await create_book()
    assert await book_storage.count(input_dto=BookListParams(limit=10, offset=0)) == 1


async def test__count__zero(
    book_storage: BookStorage,
) -> None:
    assert await book_storage.count(input_dto=BookListParams(limit=10, offset=0)) == 0


async def test__exists_by_id(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    assert await book_storage.exists_by_id(input_id=db_book.id)


async def test__exists_by_id__false(book_storage: BookStorage) -> None:
    assert await book_storage.exists_by_id(input_id=uuid4()) is False


async def test__exists_by_id__deleted(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book(deleted_at=now_utc())
    assert await book_storage.exists_by_id(input_id=db_book.id) is False


async def test__update_by_id(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    update_data = UpdateBook(
        id=db_book.id,
        title="test_title",
        year=now_utc().year,
        author="test_author",
    )
    book = await book_storage.update_by_id(input_dto=update_data)
    assert book == Book(
        id=db_book.id,
        title=update_data.title,
        year=update_data.year,
        author=update_data.author,
        created_at=db_book.created_at,
        updated_at=IsDatetime,
    )


async def test__update_by_id__none(book_storage: BookStorage) -> None:
    with pytest.raises(EntityNotFoundException):
        await book_storage.update_by_id(
            input_dto=UpdateBook(id=uuid4(), title="test_title")
        )


async def test__update_by_id__entity_already_exists_exception(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    db_book_to_update: BookTable = await create_book()
    with pytest.raises(EntityAlreadyExistsException):
        await book_storage.update_by_id(
            input_dto=UpdateBook(
                id=db_book_to_update.id,
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
            )
        )


async def test__delete_by_id(
    book_storage: BookStorage,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    await book_storage.delete_by_id(input_id=db_book.id)
    assert db_book.deleted_at is not None
