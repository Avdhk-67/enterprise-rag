"""AWS Bedrock LLM for answer generation."""
import json
import boto3
from typing import List, Dict, Optional
from src.utils.aws_client import get_bedrock_client
from src.utils.config_loader import get_aws_config, get_env_var, get_rag_config


class BedrockLLM:
    """LLM wrapper for AWS Bedrock Claude models."""
    
    def __init__(self, model_id: Optional[str] = None):
        self.bedrock_client = get_bedrock_client()
        self.config = get_aws_config()
        self.rag_config = get_rag_config()
        
        if model_id:
            self.model_id = model_id
        else:
            self.model_id = get_env_var(
                "BEDROCK_MODEL_ID",
                self.config.get("bedrock", {}).get("models", {}).get("generation", {}).get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0")
            )
        
        gen_config = self.rag_config.get("generation", {})
        self.temperature = gen_config.get("temperature", 0.0)
        self.max_tokens = gen_config.get("max_tokens", 2000)
        self.system_prompt = gen_config.get("system_prompt", "")
    
    def generate(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM."""
        messages = []
        
        # Add context if provided
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {prompt}\n\nAnswer based on the context above. If the answer is not in the context, say so."
        else:
            user_content = prompt
        
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_content}]
        })
        
        # System prompt goes in top-level body for Claude 3
        system = system_prompt or self.system_prompt
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }
        
        if system:
            body["system"] = system
        
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def generate_with_sources(self, query: str, retrieved_docs: List[Dict], use_cot: bool = False) -> Dict:
        """Generate answer with source citations."""
        # Combine retrieved documents as context
        context_parts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs):
            context_parts.append(f"[Document {i+1}]\n{doc['text']}")
            sources.append({
                'chunk_id': doc.get('chunk_id'),
                'metadata': doc.get('metadata', {}),
                'similarity': doc.get('similarity', 0.0)
            })
        
        context = "\n\n".join(context_parts)
        
        # Enhanced system prompt for citations
        if use_cot:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
You must use Chain-of-Thought reasoning to answer the question.
1. First, analyze the question and the provided documents.
2. Think through the answer step-by-step.
3. Finally, provide the answer citing your sources using [Document X] format.

If the answer is not in the context, explicitly state that the information is not available.
Be accurate, concise, and professional."""
        else:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
Always cite your sources using [Document X] format.
If the answer is not in the context, explicitly state that the information is not available.
Be accurate, concise, and professional."""
        
        answer = self.generate(query, context, system_prompt)
        
        return {
            'answer': answer,
            'sources': sources,
            'context_used': len(retrieved_docs)
        }

