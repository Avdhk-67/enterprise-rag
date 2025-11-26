"""Document processor for parsing and processing various document formats."""
import io
from typing import List, Dict, Optional
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from src.ingestion.s3_document_loader import S3DocumentLoader
from io import BytesIO


class DocumentProcessor:
    """Process documents from various formats."""
    
    def __init__(self):
        self.s3_loader = S3DocumentLoader()
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.txt': self._process_txt,
            '.md': self._process_txt
        }
    
    def process_document(self, s3_key: str) -> Dict:
        """Process a document from S3."""
        file_extension = Path(s3_key).suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Download document
        file_content = self.s3_loader.download_document(s3_key)
        
        # Process based on format
        processor = self.supported_formats[file_extension]
        text_content = processor(file_content)
        
        # Get metadata
        metadata = self.s3_loader.get_document_metadata(s3_key)
        
        return {
            's3_key': s3_key,
            'text': text_content,
            'metadata': metadata,
            'format': file_extension
        }
    
    def _process_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF."""
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text_parts = []
        
        for page in reader.pages:
            text_parts.append(page.extract_text())
        
        return '\n\n'.join(text_parts)
    
    def _process_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX."""
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)
        
        return '\n\n'.join(text_parts)
    
    def _process_txt(self, file_content: bytes) -> str:
        """Extract text from TXT/MD."""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return file_content.decode('latin-1')
    
    def process_all_documents(self, prefix: Optional[str] = None) -> List[Dict]:
        """Process all documents in S3 bucket."""
        documents = self.s3_loader.list_documents(prefix)
        processed_docs = []
        
        for doc_info in documents:
            try:
                processed = self.process_document(doc_info['key'])
                processed_docs.append(processed)
                print(f"Processed: {doc_info['key']}")
            except Exception as e:
                print(f"Error processing {doc_info['key']}: {str(e)}")
        
        return processed_docs


    def process_local_pdf(self, file_path: str) -> Dict:
        from PyPDF2 import PdfReader
        full_text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = '\n\n'.join(text_parts)
        return {"text": full_text, "s3_key": "local_upload", "metadata": {"source": file_path}, "format": "pdf"}


# import io
# from typing import List, Dict, Optional
# from pathlib import Path
# from PyPDF2 import PdfReader
# from docx import Document
# from src.ingestion.s3_document_loader import S3DocumentLoader


# class DocumentProcessor:
#     def __init__(self):
#         self.s3_loader = S3DocumentLoader()
#         self.supported_formats = {
#             ".pdf": self._process_pdf,
#             ".docx": self._process_docx,
#             ".txt": self._process_txt,
#             ".md": self._process_txt
#         }

#     def process_all_documents(self, prefix: Optional[str] = None) -> List[Dict]:
#         documents = self.s3_loader.list_documents(prefix)
#         processed_docs = []
#         for doc_info in documents:
#             try:
#                 processed = self.process_document(doc_info['key'])
#                 processed_docs.append(processed)
#                 print(f"Processed: {doc_info['key']}")
#             except Exception as e:
#                 print(f"Error processing {doc_info['key']}: {str(e)}")
#         return processed_docs

#     def process_document(self, s3_key: str) -> Dict:
#         file_extension = Path(s3_key).suffix.lower()

#         file_content = self.s3_loader.download_document(s3_key)
#         metadata = self.s3_loader.get_document_metadata(s3_key)

#         if file_extension == ".pdf":
#             text = self._process_pdf(file_content)
#         elif file_extension == ".docx":
#             text = self._process_docx(file_content)
#         elif file_extension in [".txt", ".md"]:
#             text = self._process_txt(file_content)
#         else:
#             raise ValueError(f"Unsupported file format {file_extension}")

#         return {
#             "s3_key": s3_key,
#             "text": text,
#             "metadata": metadata,
#             "format": file_extension
#         }

#     def _process_pdf(self, file_content: bytes) -> str:
#         pdf_file = io.BytesIO(file_content)
#         reader = PdfReader(pdf_file)
#         text = ""

#         for page in reader.pages:
#             if page.extract_text():
#                 text += page.extract_text() + "\n"

#         return text

#     def _process_docx(self, file_content: bytes) -> str:
#         docx_file = io.BytesIO(file_content)
#         doc = Document(docx_file)
#         return "\n".join(p.text for p in doc.paragraphs)

#     def _process_txt(self, file_content: bytes) -> str:
#         try:
#             return file_content.decode("utf-8")
#         except:
#             return file_content.decode("latin-1")

#     def process_local_pdf(self, file_path: str) -> Dict:
#         reader = PdfReader(file_path)
#         text = ""

#         for page in reader.pages:
#             text += page.extract_text() or ""

#         return {
#             "text": text,
#             "metadata": {"source": file_path},
#             "format": ".pdf"
#         }
