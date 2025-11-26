"""Query rewriting module."""
from typing import Dict, Optional
from src.generation.bedrock_llm import BedrockLLM

class QueryRewriter:
    """Rewrite and expand user queries for better retrieval."""
    
    def __init__(self):
        self.llm = BedrockLLM()
    
    def rewrite_query(self, query: str) -> str:
        """
        Rewrite the query to be more specific and search-friendly.
        
        Args:
            query: Original user query
            
        Returns:
            Rewritten query
        """
        prompt = f"""You are an AI assistant that optimizes queries for a search engine. 
Your goal is to rewrite the following user query to make it more specific, clear, and likely to retrieve relevant documents.
Expand the query with synonyms or related terms if helpful, but keep the core intent.
Do not answer the question, just rewrite it.

Original Query: {query}

Rewritten Query:"""
        
        try:
            # We use a lower temperature for deterministic rewriting
            # Note: We might want to pass specific params if BedrockLLM supported it per call
            rewritten = self.llm.generate(prompt, system_prompt="You are a query rewriting expert.")
            return rewritten.strip()
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return query
