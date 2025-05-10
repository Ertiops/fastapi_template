from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.entities import UNSET, Unset
from app.domains.entities.common import Pagination


@dataclass(frozen=True, kw_only=True, slots=True)
class Book:
    id: UUID
    title: str
    year: int
    author: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class BookListParams(Pagination): ...


@dataclass(frozen=True, kw_only=True, slots=True)
class BookList:
    total: int
    items: Sequence[Book]


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateBook:
    title: str
    year: int
    author: str


@dataclass(frozen=True, kw_only=True, slots=True)
class UpdateBook:
    id: UUID
    title: str | Unset = UNSET
    year: int | Unset = UNSET
    author: str | Unset = UNSET

    def to_dict(self) -> Mapping[str, Any]:
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "id" and not isinstance(getattr(self, field.name), Unset)
        }
