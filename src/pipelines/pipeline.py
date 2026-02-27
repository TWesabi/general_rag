import os
from datetime import datetime

from src.parsers.parser_pdf import parse_pdf_with_docling
from src.storage.db_setup import Document, Session


class DocumentPipeline:
    def __init__(self):
        self.session = Session()

    def close(self):
        self.session.close()

    def document_exists(self, filename):
        """Check if document exists in database"""
        return self.session.query(Document).filter_by(filename=filename).first() is not None

    def process_pdf(self, pdf_path):
        """
        Process a PDF: parse with Docling and save to database
        """
        filename = os.path.basename(pdf_path)

        print(f"\n{'='*60}")
        print(f"📄 PROCESSING: {filename}")
        print(f"{'='*60}")

        # Step 1: Check if already exists
        if self.document_exists(filename):
            print(f"📚 Document '{filename}' already exists in database!")
            doc = self.session.query(Document).filter_by(filename=filename).first()

            # Update last_accessed
            doc.last_accessed = datetime.now()
            self.session.commit()

            print(f"   Retrieved from database (original parse: {doc.created_at})")
            print(f"   Pages: {doc.page_count}, Text length: {len(doc.parsed_text)} chars")
            return doc

        # Step 2: Parse with Docling
        print("🆕 New document - parsing with Docling...")
        try:
            parsed_result = parse_pdf_with_docling(pdf_path)
        except Exception as e:
            print(f"❌ Error parsing PDF: {e}")
            return None

        # Step 3: Create database record
        print("💾 Saving to database...")
        doc = Document(
            filename=filename,
            file_path=pdf_path,
            parsed_text=parsed_result["text"],
            metadata_json=parsed_result["metadata"],
            page_count=parsed_result["page_count"],
            document_language=parsed_result["language"],
            processing_time=parsed_result["processing_time"],
        )

        # Save to database
        self.session.add(doc)
        self.session.commit()

        print(f"✅ Successfully saved '{filename}' to database!")
        print(f"   Pages: {doc.page_count}")
        print(f"   Text length: {len(doc.parsed_text)} characters")
        print(f"   Processing time: {doc.processing_time:.2f} seconds")

        return doc

    def get_document(self, filename):
        """Retrieve a document by filename"""
        return self.session.query(Document).filter_by(filename=filename).first()

    def get_all_documents(self):
        """Get all documents"""
        return self.session.query(Document).all()

    def delete_document(self, filename):
        """Delete a document"""
        doc = self.get_document(filename)
        if doc:
            self.session.delete(doc)
            self.session.commit()
            print(f"🗑️ Deleted '{filename}'")
            return True
        return False


def process_multiple_pdfs(pdf_folder):
    """
    Process all PDFs in a folder
    """
    pipeline = DocumentPipeline()

    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

    print(f"Found {len(pdf_files)} PDF files to process\n")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        pipeline.process_pdf(pdf_path)
        print()  # Empty line between documents

    pipeline.close()


# Example usage
if __name__ == "__main__":
    # Process a single PDF
    pipeline = DocumentPipeline()

    # Replace with your actual PDF path
    doc = pipeline.process_pdf(
        r"D:\Entwicklungsprojekte\local-chatbot\rag_system\docs\to_index\test.pdf"
    )

    if doc:
        print("\n📊 Document Summary:")
        print(f"   Filename: {doc.filename}")
        print(f"   Pages: {doc.page_count}")
        print(f"   Language: {doc.document_language}")
        print(f"   Text preview: {doc.parsed_text[:300]}...")

    # Show all documents in database
    print("\n📚 ALL DOCUMENTS IN DATABASE:")
    all_docs = pipeline.get_all_documents()
    for d in all_docs:
        print(f"   - {d.filename} ({d.page_count} pages, {len(d.parsed_text)} chars)")

    pipeline.close()
