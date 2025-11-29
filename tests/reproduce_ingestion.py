import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.document_processor import DocumentProcessor

class TestScannedIngestion(unittest.TestCase):
    @patch('src.ingestion.document_processor.S3DocumentLoader')
    @patch('src.ingestion.document_processor.OCRProcessor')
    @patch('src.ingestion.document_processor.PdfReader')
    def test_scanned_pdf_fallback(self, mock_pdf_reader, mock_ocr_processor, mock_s3_loader):
        print("\nTesting Scanned PDF Fallback Logic...")
        
        # Setup mocks
        processor = DocumentProcessor()
        
        # Mock S3 download to return dummy bytes
        processor.s3_loader.download_document.return_value = b"%PDF-1.4..."
        processor.s3_loader.bucket_name = "test-bucket"
        processor.s3_loader.get_document_metadata.return_value = {}
        
        # Mock PdfReader to return empty text (simulating scanned PDF)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "   " # Whitespace only
        mock_pdf_instance = mock_pdf_reader.return_value
        mock_pdf_instance.pages = [mock_page]
        
        # Mock OCR processor
        processor.ocr_processor.extract_text_from_s3_pdf.return_value = "Extracted Text From OCR"
        
        # Execute
        result = processor.process_document("raw-documents/scanned.pdf")
        
        # Verify
        # 1. Check if OCR was called
        try:
            processor.ocr_processor.extract_text_from_s3_pdf.assert_called_with("test-bucket", "raw-documents/scanned.pdf")
            print("✅ OCR Fallback triggered correctly for empty/whitespace text.")
        except AssertionError as e:
            print("❌ OCR Fallback NOT triggered.")
            raise e
        
        # 2. Check result text
        self.assertEqual(result['text'], "Extracted Text From OCR")
        print("✅ Text correctly returned from OCR.")

if __name__ == '__main__':
    unittest.main()
