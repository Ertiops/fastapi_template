from http import HTTPStatus
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from app.application.exceptions import EmptyPayloadException
from app.controllers.rest.routers.api.v1.schemas.book import (
    BookListParamsSchema,
    BookListSchema,
    BookSchema,
    CreateBookSchema,
    UpdateBookSchema,
)
from app.domains.entities.book import (
    BookListParams,
    CreateBook,
    UpdateBook,
)
from app.domains.services.book import BookService
from app.domains.uow import AbstractUow

router = APIRouter(prefix="/books", tags=["Books"], route_class=DishkaRoute)


@router.post(
    "/",
    response_model=BookSchema,
    status_code=HTTPStatus.CREATED,
    name="Create Book",
)
async def create(
    create_data: CreateBookSchema,
    *,
    service: FromDishka[BookService],
    uow: FromDishka[AbstractUow],
) -> BookSchema:
    async with uow:
        book = await service.create(
            input_dto=CreateBook(
                title=create_data.title,
                year=create_data.year,
                author=create_data.author,
            ),
        )
    return BookSchema.model_validate(book)


@router.get(
    "/{book_id}/",
    response_model=BookSchema,
    status_code=HTTPStatus.OK,
    name="Get Book by ID",
)
async def get_by_id(
    book_id: UUID,
    *,
    service: FromDishka[BookService],
    uow: FromDishka[AbstractUow],
) -> BookSchema:
    async with uow:
        book = await service.get_by_id(input_id=book_id)
    return BookSchema.model_validate(book)


@router.get(
    "/",
    response_model=BookListSchema,
    status_code=HTTPStatus.OK,
    name="Get Book List",
)
async def get_list(
    params: BookListParamsSchema = Query(),
    *,
    service: FromDishka[BookService],
    uow: FromDishka[AbstractUow],
) -> BookListSchema:
    async with uow:
        books = await service.get_list(
            input_dto=BookListParams(limit=params.limit, offset=params.offset)
        )
    return BookListSchema.model_validate(books)


@router.patch(
    "/{book_id}/",
    response_model=BookSchema,
    status_code=HTTPStatus.OK,
    name="Update Book by ID",
)
async def update_by_id(
    book_id: UUID,
    update_data: UpdateBookSchema,
    *,
    service: FromDishka[BookService],
    uow: FromDishka[AbstractUow],
) -> BookSchema:
    values = update_data.model_dump(exclude_unset=True)
    if not values:
        raise EmptyPayloadException(message="No values to update")
    async with uow:
        result = await service.update_by_id(
            input_dto=UpdateBook(id=book_id, **values),
        )
    return BookSchema.model_validate(result)


@router.delete(
    "/{book_id}/",
    status_code=HTTPStatus.NO_CONTENT,
    name="Delete Book by ID",
)
async def delete_by_id(
    book_id: UUID,
    *,
    service: FromDishka[BookService],
    uow: FromDishka[AbstractUow],
) -> None:
    async with uow:
        await service.delete_by_id(input_id=book_id)
