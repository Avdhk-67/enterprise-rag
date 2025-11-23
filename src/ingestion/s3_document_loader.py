"""S3 document loader for ingesting documents from AWS S3."""
import boto3
from typing import List, Dict, Optional
from io import BytesIO
from pathlib import Path
from src.utils.aws_client import get_s3_client
from src.utils.config_loader import get_aws_config, get_env_var


class S3DocumentLoader:
    """Load documents from S3 bucket."""
    
    def __init__(self):
        self.s3_client = get_s3_client()
        self.config = get_aws_config()
        self.bucket_name = get_env_var("S3_BUCKET_NAME", self.config.get("s3", {}).get("bucket_name"))
        self.raw_prefix = self.config.get("s3", {}).get("prefixes", {}).get("raw_documents", "raw-documents")
    
    def list_documents(self, prefix: Optional[str] = None) -> List[Dict[str, str]]:
        """List all documents in S3 bucket."""
        prefix = prefix or self.raw_prefix
        documents = []
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if not obj['Key'].endswith('/'):  # Skip directories
                            documents.append({
                                'key': obj['Key'],
                                'size': obj['Size'],
                                'last_modified': obj['LastModified'].isoformat()
                            })
            
            return documents
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []
    
    def download_document(self, s3_key: str) -> bytes:
        """Download document from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except Exception as e:
            raise Exception(f"Error downloading document {s3_key}: {str(e)}")
    
    def upload_document(self, file_content: bytes, s3_key: str) -> bool:
        """Upload document to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content
            )
            return True
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False
    
    def get_document_metadata(self, s3_key: str) -> Dict:
        """Get metadata for a document."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'content_type': response.get('ContentType', ''),
                'content_length': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                'etag': response.get('ETag', '')
            }
        except Exception as e:
            print(f"Error getting metadata: {str(e)}")
            return {}
    
    def delete_document(self, s3_key: str) -> bool:
        """Delete document from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False

