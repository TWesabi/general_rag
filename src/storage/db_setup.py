from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///documents.db", echo=True)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    file_path = Column(String)

    # Docling-specific fields
    parsed_text = Column(Text)  # The main text content
    metadata_json = Column(JSON)  # Store Docling metadata as JSON
    page_count = Column(Integer)
    document_language = Column(String)

    # Tracking fields
    created_at = Column(DateTime, default=datetime.now)
    last_accessed = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    processing_time = Column(Integer)  # How many seconds it took to parse

    def __repr__(self):
        return f"<Document(filename='{self.filename}', pages={self.page_count})>"


# Create the table
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
print("✅ Database setup complete!")
