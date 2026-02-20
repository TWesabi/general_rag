"""Docling-based document parser."""


import os
from pathlib import Path
from typing import Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter
from docling.document_converter import PdfFormatOption

from ..models.document import Document, DocumentMetadata


class DoclingParser:
    """Parser for PDF documents using Docling."""

    def __init__(self):
        """Initialize the Docling parser."""
        # Create pipeline options with OCR disabled and table structure enabled
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Disable OCR for faster processing
        pipeline_options.do_table_structure = True  # Extract table structure

        # Create PDF format option with pipeline options
        pdf_options = PdfFormatOption(pipeline_options=pipeline_options)

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_options,
            }
        )

    def parse(self, file_path: str | Path) -> Document:
        """
        Parse a document file.

        Args:
            file_path: Path to the document file

        Returns:
            Parsed Document object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file info
        file_size = file_path.stat().st_size
        file_type = file_path.suffix.lower().lstrip(".")

        # Convert document
        result = self.converter.convert(str(file_path))
        
        # Get the document from the conversion result
        doc = result.document

        # Extract text content
        text_content = doc.export_to_text()

        # Create metadata
        metadata = DocumentMetadata(
            source=str(file_path),
            file_type=file_type,
            file_size=file_size,
            custom_metadata={
                "title": getattr(doc, "title", None),
                "author": getattr(doc, "author", None),
            },
        )

        # Create document
        document = Document(
            content=text_content,
            metadata=metadata,
            raw_data=doc.model_dump() if hasattr(doc, "model_dump") else None,
        )

        return document

    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> Document:
        """
        Parse a document from bytes.

        Args:
            file_bytes: Document file content as bytes
            filename: Original filename (used to determine format)

        Returns:
            Parsed Document object
        """
        # Save to temporary file
        import tempfile

        file_type = Path(filename).suffix.lower().lstrip(".")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        try:
            return self.parse(tmp_path)
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
