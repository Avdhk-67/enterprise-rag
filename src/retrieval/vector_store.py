"""Vector store implementations for different backends."""
import os
import json
from typing import List, Dict, Optional
import numpy as np
from src.utils.config_loader import get_aws_config, get_env_var, get_rag_config
from src.embedding.bedrock_embeddings import BedrockEmbeddings


class VectorStore:
    """Abstract vector store interface."""
    
    def __init__(self):
        self.embedder = BedrockEmbeddings()
        self.config = get_aws_config()
        self.rag_config = get_rag_config()
        self.top_k = self.rag_config.get("retrieval", {}).get("top_k", 5)
        self.similarity_threshold = self.rag_config.get("retrieval", {}).get("similarity_threshold", 0.7)
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store."""
        raise NotImplementedError
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Search for similar documents."""
        raise NotImplementedError


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store for local development."""
    
    def __init__(self):
        super().__init__()
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            raise ImportError("faiss-cpu is required. Install with: pip install faiss-cpu")
        
        self.index_path = get_env_var("FAISS_INDEX_PATH", "./data/faiss_index")
        self.dimension = self.config.get("vector_db", {}).get("faiss", {}).get("dimension", 1536)
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index."""
        if os.path.exists(self.index_path):
            self.index = self.faiss.read_index(self.index_path)
            # Load metadata
            metadata_path = f"{self.index_path}.metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
        else:
            # Create new index
            self.index = self.faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to FAISS index."""
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store metadata
        for chunk in chunks:
            self.metadata.append({
                'text': chunk['text'],
                'metadata': chunk.get('metadata', {}),
                'chunk_id': chunk.get('chunk_id')
            })
        
        # Save index
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else '.', exist_ok=True)
        self.faiss.write_index(self.index, self.index_path)
        
        # Save metadata
        metadata_path = f"{self.index_path}.metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Search for similar documents."""
        top_k = top_k or self.top_k
        
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                similarity = 1 / (1 + distance)  # Convert L2 distance to similarity
                if similarity >= self.similarity_threshold:
                    result = self.metadata[idx].copy()
                    result['similarity'] = float(similarity)
                    result['distance'] = float(distance)
                    results.append(result)
        
        return results


class OpenSearchVectorStore(VectorStore):
    """OpenSearch Serverless vector store."""
    
    def __init__(self):
        super().__init__()
        try:
            from opensearchpy import OpenSearch, RequestsHttpConnection
            from requests_aws4auth import AWS4Auth
            import boto3
        except ImportError:
            raise ImportError("opensearch-py and requests-aws4auth are required")
        
        self.endpoint = get_env_var(
            "OPENSEARCH_ENDPOINT",
            self.config.get("vector_db", {}).get("opensearch", {}).get("endpoint")
        )
        self.index_name = get_env_var(
            "OPENSEARCH_INDEX_NAME",
            self.config.get("vector_db", {}).get("opensearch", {}).get("index_name", "enterprise-rag-index")
        )
        
        # Setup AWS authentication
        region = get_env_var("AWS_DEFAULT_REGION", "us-east-1")
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'aoss', session_token=credentials.token)
        
        self.client = OpenSearch(
            hosts=[{'host': self.endpoint.replace('https://', ''), 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
        
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 1536
                        },
                        "metadata": {"type": "object"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=index_body)
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to OpenSearch."""
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc = {
                'text': chunk['text'],
                'embedding': embedding,
                'metadata': chunk.get('metadata', {}),
                'chunk_id': chunk.get('chunk_id')
            }
            self.client.index(index=self.index_name, body=doc, id=chunk.get('chunk_id', i))
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Search for similar documents."""
        top_k = top_k or self.top_k
        
        query_embedding = self.embedder.embed_text(query)
        
        search_body = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k
                    }
                }
            }
        }
        
        response = self.client.search(index=self.index_name, body=search_body)
        
        results = []
        for hit in response['hits']['hits']:
            similarity = hit['_score'] / 100.0  # Normalize score
            if similarity >= self.similarity_threshold:
                results.append({
                    'text': hit['_source']['text'],
                    'metadata': hit['_source'].get('metadata', {}),
                    'chunk_id': hit['_source'].get('chunk_id'),
                    'similarity': similarity
                })
        
        return results


def get_vector_store():
    """Factory function to get appropriate vector store."""
    config = get_aws_config()
    db_type = get_env_var("VECTOR_DB_TYPE", config.get("vector_db", {}).get("type", "faiss"))
    
    if db_type == "faiss":
        return FAISSVectorStore()
    elif db_type == "opensearch":
        return OpenSearchVectorStore()
    elif db_type == "pinecone":
        # Pinecone implementation would go here
        raise NotImplementedError("Pinecone implementation coming soon")
    else:
        raise ValueError(f"Unknown vector DB type: {db_type}")

