import sys
import os
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append(os.getcwd())

# Mock missing dependencies
sys.modules['dotenv'] = MagicMock()
sys.modules['src.utils.config_loader'] = MagicMock()
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.config'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['langchain'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()

# Explicitly import modules to ensure they are available for patching
# We need to reload or import carefully since we mocked config_loader
import src.rag_pipeline
import src.processing.query_rewriter
import src.validation.quality_checker

def test_rag_enhancements():
    print("Testing RAG Enhancements...")
    
    # Mock dependencies
    with patch('src.rag_pipeline.get_vector_store') as mock_get_vs, \
         patch('src.rag_pipeline.BedrockLLM') as mock_llm_cls, \
         patch('src.processing.query_rewriter.BedrockLLM') as mock_rewriter_llm_cls, \
         patch('src.validation.quality_checker.BedrockLLM') as mock_checker_llm_cls, \
         patch('src.rag_pipeline.get_rag_config') as mock_config:
        
        # Setup mocks
        mock_vs = MagicMock()
        mock_get_vs.return_value = mock_vs
        
        # Mock Config
        config_dict = {
            "validation": {
                "min_confidence_score": 0.7,
                "similarity_threshold": 0.7
            },
            "generation": {
                "temperature": 0.0,
                "max_tokens": 2000,
                "system_prompt": ""
            }
        }
        mock_config.return_value = config_dict
        
        # Also configure the mocked module directly since QualityChecker uses it
        sys.modules['src.utils.config_loader'].get_rag_config.return_value = config_dict
        
        # Mock Vector Store Search
        mock_vs.search.return_value = [
            {'text': 'Harry Potter defeated Voldemort using Expelliarmus.', 'chunk_id': '1', 'metadata': {}, 'similarity': 0.9}
        ]
        
        # Mock LLM for Query Rewriter
        mock_rewriter_llm = MagicMock()
        mock_rewriter_llm_cls.return_value = mock_rewriter_llm
        mock_rewriter_llm.generate.return_value = "How did Harry Potter defeat Voldemort?"
        
        # Mock LLM for Generation
        mock_gen_llm = MagicMock()
        mock_llm_cls.return_value = mock_gen_llm
        mock_gen_llm.generate.return_value = "Based on the context, Harry Potter defeated Voldemort."
        
        # Mock LLM for Quality Checker
        mock_checker_llm = MagicMock()
        mock_checker_llm_cls.return_value = mock_checker_llm
        mock_checker_llm.generate.return_value = json.dumps({
            "is_grounded": True,
            "confidence": 0.95,
            "reason": "The answer is directly supported by the context."
        })
        
        # Initialize Pipeline
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        
        # Test Query
        result = pipeline.query("Harry beat Voldemort how?")
        
        # Verifications
        print("\n1. Query Rewriting:")
        mock_rewriter_llm.generate.assert_called_once()
        print(f"   Original: 'Harry beat Voldemort how?'")
        print(f"   Rewritten: '{result['rewritten_query']}'")
        assert result['rewritten_query'] == "How did Harry Potter defeat Voldemort?"
        
        print("\n2. Chain-of-Thought Generation:")
        # Check if use_cot=True was passed to generate_with_sources
        # We need to check the call args of generate_with_sources on the instance
        # But we mocked the class, so we check the instance method call if we can access it.
        # However, RAGPipeline calls self.llm.generate_with_sources. 
        # Since we mocked BedrockLLM class, self.llm is a mock.
        # But wait, BedrockLLM.generate_with_sources is a real method unless we mocked the whole class instance.
        # The patch('src.rag_pipeline.BedrockLLM') replaces the class, so pipeline.llm is a MagicMock.
        # So generate_with_sources is a mock method.
        mock_gen_llm.generate_with_sources.assert_called_once()
        call_args = mock_gen_llm.generate_with_sources.call_args
        print(f"   Called with use_cot={call_args.kwargs.get('use_cot')}")
        assert call_args.kwargs.get('use_cot') == True
        
        print("\n3. LLM-based Validation:")
        mock_checker_llm.generate.assert_called()
        print(f"   Validation Result: {result['validation']}")
        assert result['validation']['grounding']['is_grounded'] == True
        
        print("\nSUCCESS: All enhancements verified!")

if __name__ == "__main__":
    test_rag_enhancements()
