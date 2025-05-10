from collections.abc import Sequence
from datetime import UTC, datetime
from typing import NoReturn
from uuid import UUID

from sqlalchemy import exists, func, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.converters.book import convert_book_table_to_dto
from app.adapters.database.tables import BookTable
from app.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    StorageException,
)
from app.domains.entities.book import (
    Book,
    BookListParams,
    CreateBook,
    UpdateBook,
)
from app.domains.interfaces.storages.book import IBookStorage


class BookStorage(IBookStorage):
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def create(self, *, input_dto: CreateBook) -> Book:
        stmt = (
            insert(BookTable)
            .values(
                title=input_dto.title,
                year=input_dto.year,
                author=input_dto.author,
            )
            .returning(BookTable)
        )
        try:
            result = (await self.__session.scalars(stmt)).one()
        except IntegrityError as e:
            self.__raise_exception(e)
        return convert_book_table_to_dto(result=result)

    async def get_by_id(self, *, input_id: UUID) -> Book | None:
        stmt = select(BookTable).where(
            BookTable.id == input_id,
            BookTable.deleted_at.is_(None),
        )
        result = await self.__session.scalar(stmt)
        return convert_book_table_to_dto(result=result) if result else None

    async def get_list(self, *, input_dto: BookListParams) -> Sequence[Book]:
        stmt = (
            select(BookTable)
            .where(BookTable.deleted_at.is_(None))
            .limit(input_dto.limit)
            .offset(input_dto.offset)
            .order_by(BookTable.id)
        )
        result = await self.__session.scalars(stmt)
        return [convert_book_table_to_dto(result=r) for r in result]

    async def count(self, *, input_dto: BookListParams) -> int:
        stmt = (
            select(func.count())
            .select_from(BookTable)
            .where(BookTable.deleted_at.is_(None))
        )
        return await self.__session.scalar(stmt) or 0

    async def exists_by_id(self, *, input_id: UUID) -> bool:
        stmt = select(
            exists().where(BookTable.id == input_id, BookTable.deleted_at.is_(None))
        )
        return bool(await self.__session.scalar(stmt))

    async def update_by_id(self, *, input_dto: UpdateBook) -> Book:
        stmt = (
            update(BookTable)
            .where(BookTable.id == input_dto.id)
            .values(**input_dto.to_dict())
            .returning(BookTable)
        )
        try:
            result = (await self.__session.scalars(stmt)).one()
        except NoResultFound as e:
            raise EntityNotFoundException(entity=Book, entity_id=input_dto.id) from e
        except IntegrityError as e:
            self.__raise_exception(e)
        return convert_book_table_to_dto(result=result)

    async def delete_by_id(self, *, input_id: UUID) -> None:
        stmt = (
            update(BookTable)
            .where(BookTable.id == input_id)
            .values(deleted_at=datetime.now(tz=UTC))
        )
        await self.__session.execute(stmt)

    def __raise_exception(self, e: DBAPIError) -> NoReturn:
        constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
        match constraint:
            case "ix__books__title_year_author":
                raise EntityAlreadyExistsException("Book already exists") from e
        raise StorageException(self.__class__.__name__) from e
