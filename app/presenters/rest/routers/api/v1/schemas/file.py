from pydantic import AnyUrl, BaseModel


class FileSchema(BaseModel):
    url: AnyUrl
