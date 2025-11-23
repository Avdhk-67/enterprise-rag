"""Main RAG pipeline orchestrator."""
from typing import Dict, List, Optional
from src.retrieval.vector_store import get_vector_store
from src.generation.bedrock_llm import BedrockLLM
from src.validation.quality_checker import QualityChecker
from src.utils.config_loader import get_rag_config


class RAGPipeline:
    """Main RAG pipeline that orchestrates retrieval, generation, and validation."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = BedrockLLM()
        self.quality_checker = QualityChecker()
        self.config = get_rag_config()
    
    def query(self, question: str, top_k: Optional[int] = None) -> Dict:
        """Process a query through the RAG pipeline."""
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question, top_k=top_k)
        
        if not retrieved_docs:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0,
                'validation': {
                    'is_valid': False,
                    'reason': 'No relevant documents found'
                }
            }
        
        # Step 2: Generate answer with sources
        generation_result = self.llm.generate_with_sources(question, retrieved_docs)
        
        # Step 3: Validate response
        context = "\n\n".join([doc['text'] for doc in retrieved_docs])
        validation = self.quality_checker.validate_response(
            question,
            generation_result['answer'],
            retrieved_docs,
            context
        )
        
        # Step 4: Return comprehensive result
        return {
            'answer': generation_result['answer'],
            'sources': generation_result['sources'],
            'context_used': generation_result['context_used'],
            'confidence': validation['overall_score'],
            'validation': validation,
            'retrieved_docs_count': len(retrieved_docs)
        }
    
    def ingest_documents(self, documents: List[Dict]):
        """Ingest and index documents into the vector store."""
        # This would be called from the ingestion pipeline
        # Documents should already be chunked
        self.vector_store.add_documents(documents)

