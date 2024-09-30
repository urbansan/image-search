import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import DeclarativeBase  # type: ignore


class Base(DeclarativeBase):
    pass


class Image(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bytes: bytes = Column(LargeBinary, nullable=False)  # type: ignore
    thumbnail = Column(LargeBinary, nullable=True)
    hist_vector_bytes = Column(LargeBinary, nullable=True)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Timestamp for creation
    filename = Column(String(50), nullable=True)
