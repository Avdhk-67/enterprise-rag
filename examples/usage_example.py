"""Example usage of the Enterprise RAG system."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline
from src.ingestion.pipeline import IngestionPipeline


def example_ingestion():
    """Example: Ingest documents from S3."""
    print("=" * 50)
    print("Example: Document Ingestion")
    print("=" * 50)
    
    pipeline = IngestionPipeline()
    
    # Option 1: Ingest all documents with a prefix
    result = pipeline.ingest_from_s3(prefix="raw-documents/")
    print(f"\nIngestion Result:")
    print(f"  Documents processed: {result['documents_processed']}")
    print(f"  Chunks created: {result['chunks_created']}")
    print(f"  Status: {result['status']}")
    
    # Option 2: Ingest a specific document
    # result = pipeline.ingest_from_s3(s3_key="raw-documents/example.pdf")


def example_query():
    """Example: Query the knowledge base."""
    print("\n" + "=" * 50)
    print("Example: Querying Knowledge Base")
    print("=" * 50)
    
    rag = RAGPipeline()
    
    # Example queries
    queries = [
        "What is the company's refund policy?",
        "What are the key features of our product?",
        "How do I reset my password?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        result = rag.query(query)
        
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Sources: {len(result['sources'])} documents")
        print(f"Validation: {'✅ Valid' if result['validation']['is_valid'] else '❌ Invalid'}")


def example_complex_query():
    """Example: Complex multi-step query."""
    print("\n" + "=" * 50)
    print("Example: Complex Query")
    print("=" * 50)
    
    rag = RAGPipeline()
    
    query = "What is the process for handling customer complaints and what are the key steps?"
    
    print(f"Query: {query}")
    print("-" * 50)
    
    result = rag.query(query, top_k=10)
    
    print(f"Answer:\n{result['answer']}\n")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Retrieved {result['retrieved_docs_count']} documents")
    print(f"\nSources:")
    for i, source in enumerate(result['sources'][:3], 1):
        print(f"  {i}. Similarity: {source['similarity']:.2f}")
        print(f"     Metadata: {source.get('metadata', {})}")


if __name__ == "__main__":
    print("Enterprise RAG System - Usage Examples\n")
    
    # Uncomment the examples you want to run
    
    # Example 1: Ingest documents
    # example_ingestion()
    
    # Example 2: Simple queries
    example_query()
    
    # Example 3: Complex queries
    # example_complex_query()

