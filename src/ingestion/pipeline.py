"""Complete ingestion pipeline from S3 to vector store."""
from typing import List, Optional, Dict
from src.ingestion.s3_document_loader import S3DocumentLoader
from src.ingestion.document_processor import DocumentProcessor
from src.processing.chunker import DocumentChunker
from src.embedding.bedrock_embeddings import BedrockEmbeddings
from src.retrieval.vector_store import get_vector_store


class IngestionPipeline:
    """Complete pipeline for ingesting documents from S3."""
    
    def __init__(self):
        self.s3_loader = S3DocumentLoader()
        self.doc_processor = DocumentProcessor()
        self.chunker = DocumentChunker()
        self.vector_store = get_vector_store()
    
    def ingest_from_s3(self, s3_key: Optional[str] = None, prefix: Optional[str] = None) -> Dict:
        """Ingest documents from S3 and add to vector store."""
        if s3_key:
            # Process single document
            documents = [self.doc_processor.process_document(s3_key)]
        else:
            # Process all documents with prefix
            documents = self.doc_processor.process_all_documents(prefix)
        
        all_chunks = []
        
        for doc in documents:
            # Chunk document
            chunks = self.chunker.chunk_document(
                doc['text'],
                metadata={
                    's3_key': doc['s3_key'],
                    'format': doc['format'],
                    **doc['metadata']
                }
            )
            all_chunks.extend(chunks)
        
        # Add to vector store
        if all_chunks:
            self.vector_store.add_documents(all_chunks)
        
        return {
            'documents_processed': len(documents),
            'chunks_created': len(all_chunks),
            'status': 'success'
        }
    
    def ingest_local_file(self, file_path: str, s3_key: Optional[str] = None) -> Dict:
        """Ingest a local file (optionally upload to S3 first)."""
        # Read local file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Upload to S3 if s3_key provided
        if s3_key:
            self.s3_loader.upload_document(file_content, s3_key)
            return self.ingest_from_s3(s3_key=s3_key)
        else:
            # Process directly without S3
            # This is a simplified version - in production, you'd want proper format detection
            from pathlib import Path
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                from src.ingestion.document_processor import DocumentProcessor
                processor = DocumentProcessor()
                # Create a temporary document dict
                doc = processor._process_pdf(file_content)
                chunks = self.chunker.chunk_document(doc, metadata={'source': file_path})
                self.vector_store.add_documents(chunks)
                return {'chunks_created': len(chunks), 'status': 'success'}
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

