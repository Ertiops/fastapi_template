from uuid import UUID

from app.application.exceptions import EntityNotFoundException
from app.domains.entities.user import (
    CreateUser,
    UpdateUser,
    User,
    UserList,
    UserListParams,
)
from app.domains.interfaces.storages.user import IUserStorage


class UserService:
    __user_storage: IUserStorage

    def __init__(self, user_storage: IUserStorage) -> None:
        self.__user_storage = user_storage

    async def create(self, *, input_dto: CreateUser) -> User:
        return await self.__user_storage.create(input_dto=input_dto)

    async def get_by_id(self, *, input_id: UUID) -> User:
        user = await self.__user_storage.get_by_id(input_id=input_id)
        if user is None:
            raise EntityNotFoundException(entity=User, entity_id=input_id)
        return user

    async def get_list(self, *, input_dto: UserListParams) -> UserList:
        total = await self.__user_storage.count(input_dto=input_dto)
        items = await self.__user_storage.get_list(input_dto=input_dto)
        return UserList(total=total, items=items)

    async def update_by_id(self, *, input_dto: UpdateUser) -> User:
        if not await self.__user_storage.exists_by_id(input_id=input_dto.id):
            raise EntityNotFoundException(entity=User, entity_id=input_dto.id)
        return await self.__user_storage.update_by_id(input_dto=input_dto)

    async def delete_by_id(self, *, input_id: UUID) -> None:
        if not await self.__user_storage.exists_by_id(input_id=input_id):
            raise EntityNotFoundException(entity=User, entity_id=input_id)
        await self.__user_storage.delete_by_id(input_id=input_id)
