"""OCR Processor using AWS Textract."""
import io
import boto3
from typing import Optional, List, Dict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


class OCRProcessor:
    """Handles OCR processing using AWS Textract and PDF generation."""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.textract = boto3.client('textract', region_name=region_name)
    
    def extract_text_from_bytes(self, file_content: bytes) -> str:
        """
        Extract text from image bytes using AWS Textract.
        
        Args:
            file_content: Raw bytes of the image/document
            
        Returns:
            Extracted text string
        """
        try:
            response = self.textract.detect_document_text(
                Document={'Bytes': file_content}
            )
            
            lines = []
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    lines.append(item['Text'])
            
            return '\n'.join(lines)
            
        except Exception as e:
            print(f"Error calling Textract: {str(e)}")
            raise

    def extract_text_from_s3_pdf(self, bucket: str, key: str) -> str:
        """
        Extract text from a PDF in S3 using AWS Textract (Async API).
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            Extracted text string
        """
        import time
        
        try:
            # Start the job
            response = self.textract.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            job_id = response['JobId']
            print(f"Started Textract job {job_id} for {key}")
            
            # Wait for the job to complete
            while True:
                response = self.textract.get_document_text_detection(JobId=job_id)
                status = response['JobStatus']
                
                if status in ['SUCCEEDED', 'FAILED']:
                    break
                
                print(f"Waiting for Textract job {job_id}...")
                time.sleep(2)
            
            if status == 'FAILED':
                raise Exception(f"Textract job {job_id} failed")
            
            # Extract text from all pages
            lines = []
            
            # Helper to process blocks
            def process_blocks(blocks):
                for item in blocks:
                    if item['BlockType'] == 'LINE':
                        lines.append(item['Text'])
            
            process_blocks(response['Blocks'])
            
            # Handle pagination if multiple pages of results
            next_token = response.get('NextToken')
            while next_token:
                response = self.textract.get_document_text_detection(
                    JobId=job_id,
                    NextToken=next_token
                )
                process_blocks(response['Blocks'])
                next_token = response.get('NextToken')
            
            return '\n'.join(lines)
            
        except Exception as e:
            print(f"Error in PDF OCR: {str(e)}")
            raise
            
    def create_text_pdf(self, text: str, output_path: str) -> str:
        """
        Create a simple PDF containing the provided text.
        
        Args:
            text: Text to write to PDF
            output_path: Path to save the PDF
            
        Returns:
            Path to the created PDF
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Simple text wrapping and writing
        text_object = c.beginText()
        text_object.setTextOrigin(inch, height - inch)
        text_object.setFont("Helvetica", 12)
        
        # Split text into lines and handle basic wrapping
        # This is a basic implementation; for complex layouts, we might need Platypus
        lines = text.split('\n')
        
        for line in lines:
            # Check if we need a new page (rough estimation)
            if text_object.getY() < inch:
                c.drawText(text_object)
                c.showPage()
                text_object = c.beginText()
                text_object.setTextOrigin(inch, height - inch)
                text_object.setFont("Helvetica", 12)
            
            text_object.textLine(line)
            
        c.drawText(text_object)
        c.save()
        
        return output_path
