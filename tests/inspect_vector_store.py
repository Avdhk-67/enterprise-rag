import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retrieval.vector_store import get_vector_store

def inspect_store():
    load_dotenv()
    store = get_vector_store()
    
    print(f"Total documents: {store.index.ntotal}")
    
    # FAISS store in this project might store metadata in a separate dict or list
    # Let's check how metadata is stored in src/retrieval/vector_store.py
    # Assuming it has a .docstore or similar if it's LangChain based, 
    # or a custom implementation.
    
    # Based on previous file views, it seems to use a custom wrapper or LangChain.
    # Let's try to access the docstore if available.
    
    if hasattr(store, 'docstore'):
        print("\nDocument IDs in store:")
        for doc_id, doc in store.docstore._dict.items():
            source = doc.metadata.get('s3_key') or doc.metadata.get('source')
            print(f"- {source}")
    else:
        print("Could not directly access docstore. Trying to search for the file...")
        # results = store.search("affidavit", top_k=10)
        print("\nDirectly inspecting metadata list:")
        for i, meta in enumerate(store.metadata):
             print(f"[{i}] {meta.get('metadata', {}).get('s3_key', 'Unknown')} (Len: {len(meta.get('text', ''))})")

if __name__ == "__main__":
    inspect_store()
