import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import RAGPipeline

def query_system(question):
    load_dotenv()
    print(f"Querying system with: '{question}'")
    
    rag = RAGPipeline()
    
    try:
        result = rag.query(question)
        print("\n✅ Query Successful!")
        print(f"Answer: {result['answer']}")
        print("\nSources:")
        for source in result['sources']:
            print(f"- {source['metadata'].get('s3_key', 'Unknown')} (Score: {source.get('score', source.get('similarity', 'N/A'))})")
            
    except Exception as e:
        print(f"\n❌ Query Failed: {str(e)}")

if __name__ == "__main__":
    # Default question relevant to an Affidavit or general document
    question = "What is this document about?"
    if len(sys.argv) > 1:
        question = sys.argv[1]
        
    query_system(question)
