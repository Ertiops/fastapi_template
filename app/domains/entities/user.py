from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.entities import UNSET, Unset
from app.domains.entities.common import Pagination


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
class CreateUser:
    username: str
    email: str


@dataclass(frozen=True, kw_only=True, slots=True)
class UpdateUser:
    id: UUID
    username: str | Unset = UNSET
    email: str | Unset = UNSET

    def to_dict(self) -> Mapping[str, Any]:
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "id" and not isinstance(getattr(self, field.name), Unset)
        }
