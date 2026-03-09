import enum
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class DocumentStatus(str, enum.Enum):
    PARSED = "parsed"
    CLEANED = "cleaned"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_name: Mapped[str] = mapped_column(nullable=False)
    filename: Mapped[str | None]
    binary_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    mimetype: Mapped[str | None]
    local_path: Mapped[str | None]
    num_pages: Mapped[str | None]
    status: Mapped[DocumentStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    hints: Mapped[str | None]
    has_table: Mapped[bool | None]
    has_image: Mapped[bool | None]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
