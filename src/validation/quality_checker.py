"""Quality validation for RAG responses."""
from typing import Dict, List
from src.generation.bedrock_llm import BedrockLLM
from src.utils.config_loader import get_rag_config


class QualityChecker:
    """Validate RAG responses for quality, relevancy, and grounding."""
    
    def __init__(self):
        self.llm = BedrockLLM()
        self.config = get_rag_config()
        self.validation_config = self.config.get("validation", {})
        self.min_confidence = self.validation_config.get("min_confidence_score", 0.7)
    
    def check_relevancy(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """Check if retrieved documents are relevant to the query."""
        if not retrieved_docs:
            return {
                'is_relevant': False,
                'score': 0.0,
                'reason': 'No documents retrieved'
            }
        
        # Calculate average similarity
        avg_similarity = sum(doc.get('similarity', 0.0) for doc in retrieved_docs) / len(retrieved_docs)
        
        is_relevant = avg_similarity >= self.validation_config.get("similarity_threshold", 0.7)
        
        return {
            'is_relevant': is_relevant,
            'score': avg_similarity,
            'reason': f'Average similarity: {avg_similarity:.2f}'
        }
    
    def check_grounding(self, answer: str, context: str) -> Dict:
        """Check if answer is grounded in the provided context."""
        prompt = f"""Analyze if the following answer is grounded in the provided context.

Context:
{context}

Answer:
{answer}

Respond with JSON:
{{
    "is_grounded": true/false,
    "confidence": 0.0-1.0,
    "reason": "explanation"
}}"""
        
        try:
            response = self.llm.generate(prompt)
            # Parse JSON response (simplified - in production, use proper JSON parsing)
            # For now, return a basic check
            context_lower = context.lower()
            answer_lower = answer.lower()
            
            # Simple heuristic: check if key terms from answer appear in context
            answer_words = set(answer_lower.split())
            context_words = set(context_lower.split())
            overlap = len(answer_words.intersection(context_words)) / max(len(answer_words), 1)
            
            is_grounded = overlap > 0.3 and "not available" not in answer_lower and "not in the context" not in answer_lower
            
            return {
                'is_grounded': is_grounded,
                'confidence': min(overlap * 2, 1.0),
                'reason': f'Term overlap: {overlap:.2f}'
            }
        except Exception as e:
            return {
                'is_grounded': False,
                'confidence': 0.0,
                'reason': f'Error checking grounding: {str(e)}'
            }
    
    def check_hallucination(self, answer: str, context: str) -> Dict:
        """Check for potential hallucinations."""
        # Similar to grounding check but more strict
        grounding_result = self.check_grounding(answer, context)
        
        # Additional checks
        has_uncertainty_phrases = any(phrase in answer.lower() for phrase in [
            "not available", "not in the context", "cannot find", "not found"
        ])
        
        is_hallucination = not grounding_result['is_grounded'] and not has_uncertainty_phrases
        
        return {
            'is_hallucination': is_hallucination,
            'confidence': 1.0 - grounding_result['confidence'],
            'reason': 'Answer may contain information not in context'
        }
    
    def validate_response(self, query: str, answer: str, retrieved_docs: List[Dict], context: str) -> Dict:
        """Comprehensive validation of RAG response."""
        relevancy = self.check_relevancy(query, retrieved_docs)
        grounding = self.check_grounding(answer, context)
        hallucination = self.check_hallucination(answer, context)
        
        overall_score = (
            relevancy['score'] * 0.3 +
            grounding['confidence'] * 0.5 +
            (1 - hallucination['confidence']) * 0.2
        )
        
        is_valid = (
            relevancy['is_relevant'] and
            grounding['is_grounded'] and
            not hallucination['is_hallucination'] and
            overall_score >= self.min_confidence
        )
        
        return {
            'is_valid': is_valid,
            'overall_score': overall_score,
            'relevancy': relevancy,
            'grounding': grounding,
            'hallucination': hallucination
        }

