from http import HTTPStatus
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from app.application.exceptions import EmptyPayloadException
from app.controllers.rest.routers.api.v1.schemas.user import (
    CreateUserSchema,
    UpdateUserSchema,
    UserListParamsSchema,
    UserListSchema,
    UserSchema,
)
from app.domains.entities.user import (
    CreateUser,
    UpdateUser,
    UserListParams,
)
from app.domains.services.user import UserService
from app.domains.uow import AbstractUow

router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)


@router.post(
    "/",
    response_model=UserSchema,
    status_code=HTTPStatus.CREATED,
    name="Create User",
)
async def create(
    create_data: CreateUserSchema,
    *,
    service: FromDishka[UserService],
    uow: FromDishka[AbstractUow],
) -> UserSchema:
    async with uow:
        result = await service.create(
            input_dto=CreateUser(**create_data.model_dump()),
        )
    return UserSchema.model_validate(result)


@router.get(
    "/{user_id}/",
    response_model=UserSchema,
    status_code=HTTPStatus.OK,
    name="Get User by ID",
)
async def get_by_id(
    user_id: UUID,
    *,
    service: FromDishka[UserService],
    uow: FromDishka[AbstractUow],
) -> UserSchema:
    async with uow:
        result = await service.get_by_id(input_id=user_id)
    return UserSchema.model_validate(result)


@router.get(
    "/",
    response_model=UserListSchema,
    status_code=HTTPStatus.OK,
    name="Get User List",
)
async def get_list(
    params: UserListParamsSchema = Query(),
    *,
    service: FromDishka[UserService],
    uow: FromDishka[AbstractUow],
) -> UserListSchema:
    async with uow:
        result = await service.get_list(
            input_dto=UserListParams(**params.model_dump()),
        )
    return UserListSchema.model_validate(result)


@router.patch(
    "/{user_id}/",
    response_model=UserSchema,
    status_code=HTTPStatus.OK,
    name="Update User by ID",
)
async def update_by_id(
    user_id: UUID,
    update_data: UpdateUserSchema,
    *,
    service: FromDishka[UserService],
    uow: FromDishka[AbstractUow],
) -> UserSchema:
    values = update_data.model_dump(exclude_unset=True)
    if not values:
        raise EmptyPayloadException(message="No values to update")
    async with uow:
        result = await service.update_by_id(
            input_dto=UpdateUser(id=user_id, **values),
        )
    return UserSchema.model_validate(result)


@router.delete(
    "/{user_id}/",
    status_code=HTTPStatus.NO_CONTENT,
    name="Delete User by ID",
)
async def delete_by_id(
    user_id: UUID,
    *,
    service: FromDishka[UserService],
    uow: FromDishka[AbstractUow],
) -> None:
    async with uow:
        await service.delete_by_id(input_id=user_id)
