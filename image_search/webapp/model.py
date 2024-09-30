from pydantic import BaseModel


class ImageUploaded(BaseModel):
    image_id: str
    filename: str


class ImageIds(BaseModel):
    image_ids: list[str]
