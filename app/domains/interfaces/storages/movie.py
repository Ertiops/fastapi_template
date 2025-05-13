from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domains.entities.movie import (
    CreateMovie,
    Movie,
    MovieListParams,
    UpdateMovie,
)


class IMovieStorage(Protocol):
    @abstractmethod
    async def create(self, *, input_dto: CreateMovie) -> Movie:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *, input_id: UUID) -> Movie | None:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *, input_dto: MovieListParams) -> Sequence[Movie]:
        raise NotImplementedError

    @abstractmethod
    async def count(self, *, input_dto: MovieListParams) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, *, input_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update_by_id(self, *, input_dto: UpdateMovie) -> Movie:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, *, input_id: UUID) -> None:
        raise NotImplementedError
