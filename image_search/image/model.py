from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.engine import Row


class ImageIn(BaseModel):
    data: bytes


class ImageDto(BaseModel):
    id: str
    bytes_: bytes
    thumbnail: bytes | None
    hist_vector_bytes: bytes | None
    size: int
    created_at: datetime
    filename: str

    @property
    def is_processed(self):
        return self.thumbnail is not None and self.hist_vector_bytes is not None

    @classmethod
    def from_row(cls, row: Row):
        return cls(
            id=row.id,
            bytes_=row.bytes,
            thumbnail=row.thumbnail,
            hist_vector_bytes=row.hist_vector_bytes,
            size=row.size,
            created_at=row.created_at,
            filename=row.filename,
        )
