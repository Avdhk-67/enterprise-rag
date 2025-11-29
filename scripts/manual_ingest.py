import sys
import os
import asyncio
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.pipeline import IngestionPipeline

def ingest_file(s3_key):
    load_dotenv()
    print(f"Starting ingestion for: {s3_key}")
    
    pipeline = IngestionPipeline()
    
    try:
        # We use the synchronous ingest_from_s3 method
        result = pipeline.ingest_from_s3(s3_key=s3_key)
        print("\n✅ Ingestion Complete!")
        print(f"Documents Processed: {result['documents_processed']}")
        print(f"Chunks Created: {result['chunks_created']}")
        print(f"Status: {result['status']}")
        
    except Exception as e:
        print(f"\n❌ Ingestion Failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/manual_ingest.py <s3_key>")
        print("Example: python scripts/manual_ingest.py raw-documents/scanned_file.pdf")
        sys.exit(1)
        
    s3_key = sys.argv[1]
    ingest_file(s3_key)
