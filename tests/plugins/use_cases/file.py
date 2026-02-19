import pytest

from app.domain.interfaces.storages.file import IFileStorage
from app.domain.uow import AbstractUow
from app.domain.use_cases.file.upload import UploadFileUC


@pytest.fixture
def upload_file_uc(uow: AbstractUow, s3_storage: IFileStorage) -> UploadFileUC:
    return UploadFileUC(
        uow=uow,
        file_storage=s3_storage,
    )
