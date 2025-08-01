from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities.user import (
    CreateUser,
    UpdateUser,
    User,
    UserListParams,
)


class IUserStorage(Protocol):
    @abstractmethod
    async def create(self, *, input_dto: CreateUser) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *, input_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *, input_dto: UserListParams) -> Sequence[User]:
        raise NotImplementedError

    @abstractmethod
    async def count(self, *, input_dto: UserListParams) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, *, input_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update_by_id(self, *, input_dto: UpdateUser) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, *, input_id: UUID) -> None:
        raise NotImplementedError
