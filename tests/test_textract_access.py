import boto3
import os
import base64
from dotenv import load_dotenv

def test_textract_access():
    load_dotenv()
    
    print("Testing AWS Textract Access...")
    
    try:
        # Initialize Textract client
        # It will automatically use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        textract = boto3.client('textract', region_name=region)
        
        print(f"Attempting to connect to Textract in region: {region}")
        
        # 1x1 white pixel JPEG
        b64_image = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q=="
        dummy_image_bytes = base64.b64decode(b64_image)
        
        response = textract.detect_document_text(
            Document={'Bytes': dummy_image_bytes}
        )
        
        print("\n✅ SUCCESS: Successfully connected to AWS Textract!")
        print(f"Request ID: {response['ResponseMetadata']['RequestId']}")
        print("Your IAM permissions are correctly configured.")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to AWS Textract.")
        print(f"Error details: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if AWS_DEFAULT_REGION in .env matches the region you are using.")
        print("2. Verify that the IAM policy is attached to the correct user.")
        print("3. Ensure your AWS keys in .env are correct.")

if __name__ == "__main__":
    test_textract_access()
