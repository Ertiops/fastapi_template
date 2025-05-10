from uuid import UUID

from app.application.exceptions import EntityNotFoundException
from app.domains.entities.book import (
    Book,
    BookList,
    BookListParams,
    CreateBook,
    UpdateBook,
)
from app.domains.interfaces.storages.book import IBookStorage


class BookService:
    __book_storage: IBookStorage

    def __init__(self, book_storage: IBookStorage) -> None:
        self.__book_storage = book_storage

    async def create(self, *, input_dto: CreateBook) -> Book:
        return await self.__book_storage.create(input_dto=input_dto)

    async def get_by_id(self, *, input_id: UUID) -> Book:
        book = await self.__book_storage.get_by_id(input_id=input_id)
        if book is None:
            raise EntityNotFoundException(entity=Book, entity_id=input_id)
        return book

    async def get_list(self, *, input_dto: BookListParams) -> BookList:
        total = await self.__book_storage.count(input_dto=input_dto)
        items = await self.__book_storage.get_list(input_dto=input_dto)
        return BookList(total=total, items=items)

    async def update_by_id(self, *, input_dto: UpdateBook) -> Book:
        if not await self.__book_storage.exists_by_id(input_id=input_dto.id):
            raise EntityNotFoundException(entity=Book, entity_id=input_dto.id)
        return await self.__book_storage.update_by_id(input_dto=input_dto)

    async def delete_by_id(self, *, input_id: UUID) -> None:
        if not await self.__book_storage.exists_by_id(input_id=input_id):
            raise EntityNotFoundException(entity=Book, entity_id=input_id)
        await self.__book_storage.delete_by_id(input_id=input_id)
