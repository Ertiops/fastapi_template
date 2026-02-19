from http import HTTPStatus
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, cast

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, Form, UploadFile

from app.domain.entities.file import UploadFileToStorage
from app.domain.use_cases.file.upload import UploadFileUC
from app.presenters.rest.routers.api.v1.schemas.file import UploadedFileUrlSchema

router = APIRouter(prefix="/files", tags=["Files"], route_class=DishkaRoute)

READ_CHUNK_SIZE = 1024 * 1024
MAX_SPOOLED_MEMORY_SIZE = 1024 * 1024


@router.post(
    "/upload/",
    response_model=UploadedFileUrlSchema,
    status_code=HTTPStatus.OK,
    name="Upload File",
)
async def upload_file(
    entity: str = Form(...),
    file: UploadFile = File(...),
    *,
    use_case: FromDishka[UploadFileUC],
) -> UploadedFileUrlSchema:
    with SpooledTemporaryFile(max_size=MAX_SPOOLED_MEMORY_SIZE, mode="w+b") as stream:
        while True:
            chunk = await file.read(READ_CHUNK_SIZE)
            if not chunk:
                break
            stream.write(chunk)

        stream.seek(0)
        result = await use_case.execute(
            input_dto=UploadFileToStorage(
                entity=entity,
                file=cast(BinaryIO, stream),
                content_type=file.content_type or "application/octet-stream",
                filename=file.filename,
                public_read=True,
                metadata=None,
            )
        )

    return UploadedFileUrlSchema(file_url=result.file_url)
