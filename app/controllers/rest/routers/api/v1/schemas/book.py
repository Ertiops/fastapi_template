from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from pydantic import Field, PositiveInt

from app.controllers.rest.schemas import BaseSchema, PaginationSchema


class BookSchema(BaseSchema):
    id: UUID
    title: str
    year: int
    author: str
    created_at: datetime
    updated_at: datetime


class BookListParamsSchema(PaginationSchema): ...


class BookListSchema(BaseSchema):
    total: int
    items: Sequence[BookSchema]


class CreateBookSchema(BaseSchema):
    title: str = Field(min_length=3, max_length=255)
    year: PositiveInt = Field(ge=0, le=datetime.now(tz=UTC).year)
    author: str = Field(min_length=3, max_length=255)


class UpdateBookSchema(BaseSchema):
    title: str | None = Field(min_length=3, max_length=255, default=None)
    year: int | None = Field(ge=0, le=datetime.now(tz=UTC).year, default=None)
    author: str | None = Field(min_length=3, max_length=255, default=None)
