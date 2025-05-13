from http import HTTPStatus
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from app.application.exceptions import EmptyPayloadException
from app.domains.entities.movie import (
    CreateMovie,
    MovieListParams,
    UpdateMovie,
)
from app.domains.services.movie import MovieService
from app.domains.uow import AbstractUow
from app.presenters.rest.routers.api.v1.schemas.movie import (
    CreateMovieSchema,
    MovieListParamsSchema,
    MovieListSchema,
    MovieSchema,
    UpdateMovieSchema,
)

router = APIRouter(prefix="/movies", tags=["Movies"], route_class=DishkaRoute)


@router.post(
    "/",
    response_model=MovieSchema,
    status_code=HTTPStatus.CREATED,
    name="Create Movie",
)
async def create(
    create_data: CreateMovieSchema,
    *,
    service: FromDishka[MovieService],
    uow: FromDishka[AbstractUow],
) -> MovieSchema:
    async with uow:
        result = await service.create(input_dto=CreateMovie(**create_data.model_dump()))
    return MovieSchema.model_validate(result)


@router.get(
    "/{movie_id}/",
    response_model=MovieSchema,
    status_code=HTTPStatus.OK,
    name="Get Movie by ID",
)
async def get_by_id(
    movie_id: UUID,
    *,
    service: FromDishka[MovieService],
    uow: FromDishka[AbstractUow],
) -> MovieSchema:
    async with uow:
        result = await service.get_by_id(input_id=movie_id)
    return MovieSchema.model_validate(result)


@router.get(
    "/",
    response_model=MovieListSchema,
    status_code=HTTPStatus.OK,
    name="Get Movie List",
)
async def get_list(
    params: MovieListParamsSchema = Query(),
    *,
    service: FromDishka[MovieService],
    uow: FromDishka[AbstractUow],
) -> MovieListSchema:
    async with uow:
        result = await service.get_list(
            input_dto=MovieListParams(limit=params.limit, offset=params.offset)
        )
    return MovieListSchema.model_validate(result)


@router.patch(
    "/{movie_id}/",
    response_model=MovieSchema,
    status_code=HTTPStatus.OK,
    name="Update Movie by ID",
)
async def update_by_id(
    movie_id: UUID,
    update_data: UpdateMovieSchema,
    *,
    service: FromDishka[MovieService],
    uow: FromDishka[AbstractUow],
) -> MovieSchema:
    values = update_data.model_dump(exclude_unset=True)
    if not values:
        raise EmptyPayloadException(message="No values to update")
    async with uow:
        result = await service.update_by_id(
            input_dto=UpdateMovie(id=movie_id, **values),
        )
    return MovieSchema.model_validate(result)


@router.delete(
    "/{movie_id}/",
    status_code=HTTPStatus.NO_CONTENT,
    name="Delete Movie by ID",
)
async def delete_by_id(
    movie_id: UUID,
    *,
    service: FromDishka[MovieService],
    uow: FromDishka[AbstractUow],
) -> None:
    async with uow:
        await service.delete_by_id(input_id=movie_id)
