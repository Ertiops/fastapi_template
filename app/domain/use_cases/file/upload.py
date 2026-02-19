from app.application.use_case import IUseCase
from app.domain.entities.file import S3User, UploadFileResult, UploadFileToStorage
from app.domain.interfaces.storages.file import IFileStorage
from app.domain.uow import AbstractUow


class UploadFileUC(IUseCase[UploadFileToStorage, UploadFileResult]):
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

    async def execute(self, *, input_dto: UploadFileToStorage) -> UploadFileResult:
        async with self._uow:
            file_url = await self._file_storage.upload_file(
                input_dto=input_dto,
                user=S3User(id=None),
            )
        return UploadFileResult(file_url=file_url)
