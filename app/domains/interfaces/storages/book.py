from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domains.entities.book import (
    Book,
    BookListParams,
    CreateBook,
    UpdateBook,
)


class IBookStorage(Protocol):
    @abstractmethod
    async def create(self, *, input_dto: CreateBook) -> Book:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *, input_id: UUID) -> Book | None:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *, input_dto: BookListParams) -> Sequence[Book]:
        raise NotImplementedError

    @abstractmethod
    async def count(self, *, input_dto: BookListParams) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, *, input_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update_by_id(self, *, input_dto: UpdateBook) -> Book:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, *, input_id: UUID) -> None:
        raise NotImplementedError
