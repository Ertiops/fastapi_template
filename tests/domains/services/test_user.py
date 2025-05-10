from collections.abc import Callable
from uuid import uuid4

import pytest
from dirty_equals import IsDatetime, IsUUID

from app.adapters.database.tables import UserTable
from app.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domains.entities.user import (
    CreateUser,
    UpdateUser,
    User,
    UserList,
    UserListParams,
)
from app.domains.services.user import UserService
from tests.utils import now_utc


async def test__create(
    user_service: UserService,
) -> None:
    create_data = CreateUser(
        username="test_username",
        email="test@test.com",
    )
    user = await user_service.create(input_dto=create_data)
    assert user == User(
        id=IsUUID,
        username=create_data.username,
        email=create_data.email,
        created_at=IsDatetime,
        updated_at=IsDatetime,
    )


async def test__create__entity_already_exists_exception__username(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user()
    with pytest.raises(EntityAlreadyExistsException):
        await user_service.create(
            input_dto=CreateUser(
                username=db_user.username,
                email="test@test.com",
            )
        )


async def test__create__entity_already_exists_exception__email(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user()
    with pytest.raises(EntityAlreadyExistsException):
        await user_service.create(
            input_dto=CreateUser(
                username="test_username",
                email=db_user.email,
            )
        )


async def test__get_by_id(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user()
    user = await user_service.get_by_id(input_id=db_user.id)
    assert user == User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
    )


async def test__get_by_id__entity_not_found_exception(
    user_service: UserService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await user_service.get_by_id(input_id=uuid4())


async def test__get_by_id__entity_not_found_exception__deleted(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user(deleted_at=now_utc())
    with pytest.raises(EntityNotFoundException):
        await user_service.get_by_id(input_id=db_user.id)


async def test__get_list(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_users: list[UserTable] = [await create_user() for _ in range(2)]
    users = await user_service.get_list(input_dto=UserListParams(limit=10, offset=0))
    assert users == UserList(
        total=len(db_users),
        items=[
            User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            )
            for db_user in db_users
        ],
    )


async def test__get_list__validate_limit(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_users: list[UserTable] = [await create_user() for _ in range(2)]
    users = await user_service.get_list(input_dto=UserListParams(limit=1, offset=0))
    assert users == UserList(
        total=len(db_users),
        items=[
            User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            )
            for db_user in db_users
        ][0:1],
    )


async def test__get_list__validate_offset(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_users: list[UserTable] = [await create_user() for _ in range(2)]
    users = await user_service.get_list(input_dto=UserListParams(limit=1, offset=1))
    assert users == UserList(
        total=len(db_users),
        items=[
            User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
            )
            for db_user in db_users
        ][1:],
    )


async def test__get_list__empty_list(
    user_service: UserService,
) -> None:
    users = await user_service.get_list(input_dto=UserListParams(limit=10, offset=0))
    assert users == UserList(total=0, items=[])


async def test__update_by_id(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user()
    update_data = UpdateUser(
        id=db_user.id,
        username="test_username",
        email="test@test.com",
    )
    user = await user_service.update_by_id(input_dto=update_data)
    assert user == User(
        id=db_user.id,
        username=update_data.username,
        email=update_data.email,
        created_at=db_user.created_at,
        updated_at=IsDatetime,
    )


async def test__update_by_id__entity_not_found_exception(
    user_service: UserService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await user_service.update_by_id(
            input_dto=UpdateUser(id=uuid4(), username="test_username")
        )


async def test__delete_by_id(
    user_service: UserService,
    create_user: Callable,
) -> None:
    db_user: UserTable = await create_user()
    await user_service.delete_by_id(input_id=db_user.id)
    assert db_user.deleted_at is not None


async def test__delete_by_id__entity_not_found_exception(
    user_service: UserService,
) -> None:
    with pytest.raises(EntityNotFoundException):
        await user_service.delete_by_id(input_id=uuid4())
