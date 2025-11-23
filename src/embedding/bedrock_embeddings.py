"""AWS Bedrock embeddings for vectorization."""
import json
import boto3
from typing import List
from src.utils.aws_client import get_bedrock_client
from src.utils.config_loader import get_aws_config, get_env_var


class BedrockEmbeddings:
    """Generate embeddings using AWS Bedrock Titan model."""
    
    def __init__(self):
        self.bedrock_client = get_bedrock_client()
        self.config = get_aws_config()
        self.model_id = get_env_var(
            "BEDROCK_EMBEDDING_MODEL_ID",
            self.config.get("bedrock", {}).get("models", {}).get("embedding", {}).get("model_id", "amazon.titan-embed-text-v1")
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            body = json.dumps({"inputText": text})
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', [])
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = [self.embed_text(text) for text in batch]
            embeddings.extend(batch_embeddings)
        
        return embeddings

