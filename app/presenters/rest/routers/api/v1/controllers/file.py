from http import HTTPStatus
from typing import BinaryIO, cast

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, Form, UploadFile

from app.domain.entities.file import CreateFile, FileEntity, FileType
from app.domain.use_cases.file.upload import UploadFileUC
from app.presenters.rest.routers.api.v1.schemas.file import FileSchema

router = APIRouter(prefix="/files", tags=["Files"], route_class=DishkaRoute)


@router.post(
    "/upload/",
    response_model=FileSchema,
    status_code=HTTPStatus.OK,
    name="Upload File",
)
async def upload_file(
    entity: FileEntity = Form(...),
    file: UploadFile = File(...),
    *,
    use_case: FromDishka[UploadFileUC],
) -> FileSchema:
    file.file.seek(0)
    return FileSchema.model_validate(
        await use_case.execute(
            input_dto=CreateFile(
                entity=entity,
                file=cast(BinaryIO, file.file),
                content_type=FileType(file.content_type)
                if file.content_type
                else FileType.OCTET_STREAM,
                filename=file.filename if file.filename else "file",
                public_read=True,
                metadata={},
            )
        )
    )
