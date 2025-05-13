from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.entities import UNSET, Unset
from app.domains.entities.common import Pagination, ToDictMixin


@dataclass(frozen=True, kw_only=True, slots=True)
class User:
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class UserListParams(Pagination): ...


@dataclass(frozen=True, kw_only=True, slots=True)
class UserList:
    total: int
    items: Sequence[User]


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateUser(ToDictMixin):
    username: str
    email: str


@dataclass(frozen=True, kw_only=True, slots=True)
class UpdateUser(ToDictMixin):
    id: UUID
    username: str | Unset = UNSET
    email: str | Unset = UNSET
