from collections.abc import Callable
from uuid import UUID, uuid4

import pytest
from dirty_equals import IsDatetime, IsUUID

from app.adapters.database.tables import BookTable
from app.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domains.entities.book import (
    Book,
    BookList,
    BookListParams,
    CreateBook,
    UpdateBook,
)
from app.domains.services.book import BookService
from tests.utils import now_utc


async def test__create(book_service: BookService) -> None:
    create_data = CreateBook(
        title="test_title",
        year=now_utc().year,
        author="test_author",
    )
    book = await book_service.create(input_dto=create_data)
    assert book == Book(
        id=IsUUID,
        title=create_data.title,
        year=create_data.year,
        author=create_data.author,
        created_at=IsDatetime,
        updated_at=IsDatetime,
    )


async def test__get_by_id(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    book = await book_service.get_by_id(input_id=db_book.id)
    assert book == Book(
        id=db_book.id,
        title=db_book.title,
        year=db_book.year,
        author=db_book.author,
        created_at=db_book.created_at,
        updated_at=db_book.updated_at,
    )


async def test__get_by_id__entity_not_found_exception(
    book_service: BookService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await book_service.get_by_id(input_id=uuid4())


async def test__get_list(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    books = await book_service.get_list(input_dto=BookListParams(limit=10, offset=0))
    assert books == BookList(
        total=len(db_books),
        items=[
            Book(
                id=db_book.id,
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
                created_at=db_book.created_at,
                updated_at=db_book.updated_at,
            )
            for db_book in db_books
        ],
    )


async def test__get_list__validate_limit(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    books = await book_service.get_list(input_dto=BookListParams(limit=1, offset=0))
    assert books == BookList(
        total=len(db_books),
        items=[
            Book(
                id=db_book.id,
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
                created_at=db_book.created_at,
                updated_at=db_book.updated_at,
            )
            for db_book in db_books
        ][:1],
    )


async def test__get_list__validate_offset(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_books: list[BookTable] = [
        await create_book(id=UUID(int=i + 1)) for i in range(2)
    ]
    books = await book_service.get_list(input_dto=BookListParams(limit=2, offset=1))
    assert books == BookList(
        total=len(db_books),
        items=[
            Book(
                id=db_book.id,
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
                created_at=db_book.created_at,
                updated_at=db_book.updated_at,
            )
            for db_book in db_books
        ][1:],
    )


async def test__get_list__empty_list(book_service: BookService) -> None:
    books = await book_service.get_list(input_dto=BookListParams(limit=2, offset=1))
    assert books == BookList(total=0, items=[])


async def test__update_by_id(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    update_data = UpdateBook(
        id=db_book.id,
        title="test_title",
        year=now_utc().year,
        author="test_author",
    )
    book = await book_service.update_by_id(input_dto=update_data)
    assert book == Book(
        id=db_book.id,
        title=update_data.title,
        year=update_data.year,
        author=update_data.author,
        created_at=db_book.created_at,
        updated_at=IsDatetime,
    )


async def test__update_by_id__entity_not_found_exception(
    book_service: BookService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await book_service.update_by_id(
            input_dto=UpdateBook(
                id=uuid4(),
                title="test_title",
                year=now_utc().year,
                author="test_author",
            )
        )


async def test__update_by_id__entity_already_exists_exception(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    db_book_to_update: BookTable = await create_book()
    with pytest.raises(EntityAlreadyExistsException):
        await book_service.update_by_id(
            input_dto=UpdateBook(
                id=db_book_to_update.id,
                title=db_book.title,
                year=db_book.year,
                author=db_book.author,
            )
        )


async def test__delete_by_id(
    book_service: BookService,
    create_book: Callable,
) -> None:
    db_book: BookTable = await create_book()
    await book_service.delete_by_id(input_id=db_book.id)
    assert db_book.deleted_at is not None


async def test__delete_by_id__entity_not_found_exception(
    book_service: BookService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await book_service.delete_by_id(input_id=uuid4())
