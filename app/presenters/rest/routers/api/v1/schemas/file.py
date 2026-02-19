from pydantic import BaseModel


class UploadedFileUrlSchema(BaseModel):
    file_url: str
