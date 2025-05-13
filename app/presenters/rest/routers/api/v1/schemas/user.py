from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.presenters.rest.schemas import BaseSchema, PaginationSchema


class UserSchema(BaseSchema):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime


class UserListParamsSchema(PaginationSchema): ...


class UserListSchema(BaseSchema):
    total: int
    items: Sequence[UserSchema]


class CreateUserSchema(BaseSchema):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=3, max_length=255)


class UpdateUserSchema(BaseSchema):
    username: str | None = Field(min_length=3, max_length=255, default=None)
    email: EmailStr | None = Field(min_length=3, max_length=255, default=None)
