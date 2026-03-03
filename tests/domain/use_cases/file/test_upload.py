from io import BytesIO

from app.domain.entities.file import CreateFile
from app.domain.use_cases.file.upload import UploadFileUC


async def test__upload_file(upload_file_uc: UploadFileUC) -> None:
    result = await upload_file_uc.execute(
        input_dto=CreateFile(
            entity="avatars",
            file=BytesIO(b"image"),
            content_type="image/png",
            filename="avatar.png",
            public_read=True,
            metadata=None,
        )
    )
    assert result.url.scheme in {"http", "https"}
