from app.application.use_case import IUseCase
from app.domain.entities.user import UserList, UserListParams
from app.domain.interfaces.storages.user import IUserStorage
from app.domain.uow import AbstractUow


class GetUserListUC(IUseCase[UserListParams, UserList]):
    _user_storage: IUserStorage
    _uow: AbstractUow

    def __init__(
        self,
        uow: AbstractUow,
        user_storage: IUserStorage,
    ) -> None:
        self._user_storage = user_storage
        self._uow = uow

    async def execute(self, *, input_dto: UserListParams) -> UserList:
        async with self._uow:
            total = await self._user_storage.count(input_dto=input_dto)
            items = await self._user_storage.get_list(input_dto=input_dto)
        return UserList(total=total, items=items)
