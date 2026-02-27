import time

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def parse_pdf_with_docling(pdf_path, enable_ocr=False, enable_table_structure=False):
    """
    Parse a PDF using Docling and return both text and metadata.

    Uses lightweight options by default so parsing doesn't hang on large PDFs.
    """
    print(f"🔄 Starting Docling parse of: {pdf_path}")
    start_time = time.time()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = enable_ocr
    if hasattr(pipeline_options, "do_table_structure"):
        pipeline_options.do_table_structure = enable_table_structure
    if hasattr(pipeline_options, "do_table_structure_extraction"):
        pipeline_options.do_table_structure_extraction = enable_table_structure

    pdf_options = PdfFormatOption(pipeline_options=pipeline_options)
    converter = DocumentConverter(format_options={InputFormat.PDF: pdf_options})

    # Parse the document
    result = converter.convert(pdf_path)
    document = result.document

    # Extract text content
    text_content = document.export_to_text()

    # Extract metadata
    metadata = {
        "filename": document.name if hasattr(document, "name") else None,
        "page_count": len(document.pages) if hasattr(document, "pages") else 0,
        "languages": document.languages if hasattr(document, "languages") else [],
        "status": document.status.value if hasattr(document, "status") else None,
        "pdf_info": {
            "producer": getattr(document, "producer", None),
            "encrypted": getattr(document, "encrypted", False),
        },
    }

    # Get page count
    page_count = metadata["page_count"]

    # Try to detect language (Docling might provide this)
    document_language = metadata["languages"][0] if metadata["languages"] else "unknown"

    processing_time = time.time() - start_time

    print(f"✅ Docling parsing complete in {processing_time:.2f} seconds")
    print(f"   Pages: {page_count}, Text length: {len(text_content)} characters")

    return {
        "text": text_content,
        "metadata": metadata,
        "page_count": page_count,
        "language": document_language,
        "processing_time": processing_time,
    }


# Optional: Parse with different options
def parse_pdf_with_options(pdf_path, enable_ocr=False, enable_table_extraction=True):
    """
    Parse PDF with custom pipeline options
    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = enable_ocr
    if hasattr(pipeline_options, "do_table_structure"):
        pipeline_options.do_table_structure = enable_table_extraction
    if hasattr(pipeline_options, "do_table_structure_extraction"):
        pipeline_options.do_table_structure_extraction = enable_table_extraction

    pdf_options = PdfFormatOption(pipeline_options=pipeline_options)
    converter = DocumentConverter(format_options={InputFormat.PDF: pdf_options})
    result = converter.convert(pdf_path)
    document = result.document

    # Get both plain text and structured content
    text = document.export_to_text()
    tables = document.tables if hasattr(document, "tables") else []

    return {
        "text": text,
        "tables": [table.to_dict() for table in tables] if tables else [],
        "page_count": len(document.pages) if hasattr(document, "pages") else 0,
    }


# Test the parser
if __name__ == "__main__":
    # Replace with your actual PDF path
    result = parse_pdf_with_docling("sample.pdf")
    print(f"\nPreview of parsed text: {result['text'][:200]}...")
