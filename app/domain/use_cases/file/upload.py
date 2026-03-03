from app.application.use_case import IUseCase
from app.domain.entities.file import CreateFile, File
from app.domain.interfaces.storages.file import IFileStorage
from app.domain.uow import AbstractUow


class UploadFileUC(IUseCase[CreateFile, File]):
    _file_storage: IFileStorage
    _uow: AbstractUow

    def __init__(
        self,
        *,
        uow: AbstractUow,
        file_storage: IFileStorage,
    ) -> None:
        self._file_storage = file_storage
        self._uow = uow

    async def execute(self, *, input_dto: CreateFile) -> File:
        async with self._uow:
            url = await self._file_storage.upload_file(input_dto=input_dto)
        return File(url=url)
