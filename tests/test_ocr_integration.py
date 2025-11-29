import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.ocr_processor import OCRProcessor
from src.ingestion.document_processor import DocumentProcessor

class TestOCRIntegration(unittest.TestCase):
    
    @patch('boto3.client')
    def test_ocr_processor_image(self, mock_boto):
        # Setup mock
        mock_textract = MagicMock()
        mock_boto.return_value = mock_textract
        
        # Mock response
        mock_textract.detect_document_text.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Hello World'},
                {'BlockType': 'LINE', 'Text': 'This is a test'}
            ]
        }
        
        processor = OCRProcessor()
        text = processor.extract_text_from_bytes(b"fake_image_bytes")
        
        self.assertEqual(text, "Hello World\nThis is a test")
        
    def test_pdf_generation(self):
        processor = OCRProcessor()
        output_path = "test_output.pdf"
        
        try:
            processor.create_text_pdf("Hello World", output_path)
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(os.path.getsize(output_path), 0)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    @patch('src.ingestion.document_processor.S3DocumentLoader')
    @patch('src.ingestion.document_processor.OCRProcessor')
    def test_document_processor_image_flow(self, MockOCR, MockS3):
        # Setup mocks
        mock_s3 = MockS3.return_value
        mock_ocr = MockOCR.return_value
        
        mock_s3.download_document.return_value = b"fake_image_bytes"
        mock_s3.get_document_metadata.return_value = {}
        mock_ocr.extract_text_from_bytes.return_value = "Extracted Text"
        
        processor = DocumentProcessor()
        
        # Test processing an image
        result = processor.process_document("documents/image.jpg")
        
        # Verify OCR was called
        mock_ocr.extract_text_from_bytes.assert_called_once()
        
        # Verify PDF creation and upload
        mock_ocr.create_text_pdf.assert_called_once()
        mock_s3.upload_document.assert_called_once()
        
        # Verify result
        self.assertEqual(result['text'], "Extracted Text")
        self.assertEqual(result['format'], ".jpg")

if __name__ == '__main__':
    unittest.main()
