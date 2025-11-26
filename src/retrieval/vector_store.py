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
            try:
                self.index = self.faiss.read_index(self.index_path)
                # Load metadata
                metadata_path = f"{self.index_path}.metadata.json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.metadata = json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}. Creating new one.")
                self.index = self.faiss.IndexFlatIP(self.dimension)
                self.metadata = []
        else:
            # Create new index using Inner Product (Cosine Similarity)
            self.index = self.faiss.IndexFlatIP(self.dimension)
            self.metadata = []
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to FAISS index."""
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        # Convert to numpy array and normalize
        embeddings_array = np.array(embeddings).astype('float32')
        self.faiss.normalize_L2(embeddings_array)
        
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
        
        # Generate query embedding and normalize
        query_embedding = self.embedder.embed_text(query)
        query_vector = np.array([query_embedding]).astype('float32')
        self.faiss.normalize_L2(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata) and idx >= 0:
                # For Inner Product on normalized vectors, score IS cosine similarity
                similarity = float(score)
                if similarity >= self.similarity_threshold:
                    result = self.metadata[idx].copy()
                    result['similarity'] = similarity
                    result['distance'] = 0.0 # Not applicable for IP
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



# """Vector store implementations for different backends (FAISS, OpenSearch)."""

# import os
# import json
# from typing import List, Dict, Optional

# import numpy as np

# from src.utils.config_loader import get_aws_config, get_env_var, get_rag_config
# from src.embedding.bedrock_embeddings import BedrockEmbeddings


# # ---------------------------------------------------------------------------
# # Base interface
# # ---------------------------------------------------------------------------

# class VectorStore:
#     """Abstract vector store interface."""

#     def __init__(self):
#         self.embedder = BedrockEmbeddings()
#         self.config = get_aws_config()
#         self.rag_config = get_rag_config()

#         # Retrieval config with safe defaults
#         retrieval_cfg = self.rag_config.get("retrieval", {})
#         self.top_k = retrieval_cfg.get("top_k", 5)

#         # Make similarity_threshold optional and sane
#         # 0.2 is a MUCH more realistic default for L2-based similarity
#         self.similarity_threshold = retrieval_cfg.get("similarity_threshold", 0.2)
#         # Clamp to [0, 1]
#         self.similarity_threshold = max(0.0, min(1.0, self.similarity_threshold))

#     def add_documents(self, chunks: List[Dict]):
#         """Add document chunks to vector store."""
#         raise NotImplementedError

#     def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
#         """Search for similar documents."""
#         raise NotImplementedError


# # ---------------------------------------------------------------------------
# # FAISS implementation
# # ---------------------------------------------------------------------------

# class FAISSVectorStore(VectorStore):
#     """FAISS-based vector store for local development."""

#     def __init__(self):
#         super().__init__()
#         try:
#             import faiss  # type: ignore
#             self.faiss = faiss
#         except ImportError as e:
#             raise ImportError("faiss-cpu is required. Install with: pip install faiss-cpu") from e

#         # Where to store index + metadata
#         self.index_path = get_env_var("FAISS_INDEX_PATH", "./data/faiss_index")

#         # Vector dimension – keep config default, but allow override
#         self.dimension = (
#             self.config.get("vector_db", {})
#             .get("faiss", {})
#             .get("dimension", 1536)
#         )

#         self.index = None
#         self.metadata: List[Dict] = []
#         self._initialize_index()

#     # ----------------- internal helpers -----------------

#     def _initialize_index(self):
#         """Initialize or load FAISS index + metadata."""
#         metadata_path = f"{self.index_path}.metadata.json"

#         if os.path.exists(self.index_path):
#             try:
#                 self.index = self.faiss.read_index(self.index_path)
#                 if os.path.exists(metadata_path):
#                     with open(metadata_path, "r") as f:
#                         self.metadata = json.load(f)
#                 else:
#                     self.metadata = []
#                 print(f"[FAISS] Loaded existing index with {self.index.ntotal} vectors")
#             except Exception as e:
#                 # Corrupted index – start fresh
#                 print(f"[FAISS] Error loading existing index, recreating. Reason: {e}")
#                 self.index = self.faiss.IndexFlatL2(self.dimension)
#                 self.metadata = []
#         else:
#             # Create new index
#             os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
#             self.index = self.faiss.IndexFlatL2(self.dimension)
#             self.metadata = []
#             print("[FAISS] Created new empty index")

#     def _save(self):
#         """Persist FAISS index and metadata to disk."""
#         if self.index is None:
#             return
#         metadata_path = f"{self.index_path}.metadata.json"
#         os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
#         self.faiss.write_index(self.index, self.index_path)
#         with open(metadata_path, "w") as f:
#             json.dump(self.metadata, f)
#         print(f"[FAISS] Saved index with {self.index.ntotal} vectors")

#     # ----------------- public API -----------------

#     def add_documents(self, chunks: List[Dict]):
#         """Add document chunks to FAISS index."""

#         if not chunks:
#             print("[FAISS] add_documents called with 0 chunks, skipping")
#             return

#         texts = [chunk["text"] for chunk in chunks if chunk.get("text")]
#         if not texts:
#             print("[FAISS] No text found in chunks, skipping")
#             return

#         print(f"[FAISS] Embedding {len(texts)} chunks...")
#         embeddings = self.embedder.embed_documents(texts)

#         if not embeddings:
#             print("[FAISS] WARNING: embed_documents returned no embeddings")
#             return

#         embeddings_array = np.array(embeddings).astype("float32")

#         if embeddings_array.ndim != 2 or embeddings_array.shape[1] != self.dimension:
#             print(
#                 f"[FAISS] WARNING: Embedding dimension mismatch. "
#                 f"Expected {self.dimension}, got {embeddings_array.shape}"
#             )

#         before = self.index.ntotal
#         self.index.add(embeddings_array)
#         after = self.index.ntotal
#         print(f"[FAISS] Added vectors: before={before}, after={after}")

#         # Attach metadata entries in the same order
#         for chunk in chunks:
#             self.metadata.append(
#                 {
#                     "text": chunk["text"],
#                     "metadata": chunk.get("metadata", {}),
#                     "chunk_id": chunk.get("chunk_id"),
#                 }
#             )

#         self._save()

#     def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
#         """Search for similar documents."""

#         if self.index is None or self.index.ntotal == 0:
#             print("[FAISS] search called but index is empty")
#             return []

#         top_k = top_k or self.top_k

#         # Generate query embedding
#         print(f"[FAISS] Searching for query: {query!r}")
#         query_embedding = self.embedder.embed_text(query)
#         query_vector = np.array([query_embedding]).astype("float32")

#         # Perform search
#         distances, indices = self.index.search(query_vector, top_k)
#         print(f"[FAISS] Raw distances: {distances}")
#         print(f"[FAISS] Raw indices: {indices}")

#         results: List[Dict] = []

#         for distance, idx in zip(distances[0], indices[0]):
#             if idx < 0 or idx >= len(self.metadata):
#                 continue

#             # Convert L2 distance to a crude similarity score
#             similarity = 1.0 / (1.0 + float(distance))

#             # Optional filtering – keep this loose
#             if similarity < self.similarity_threshold:
#                 continue

#             entry = self.metadata[idx].copy()
#             entry["similarity"] = float(similarity)
#             entry["distance"] = float(distance)
#             results.append(entry)

#         print(f"[FAISS] Filtered results count: {len(results)}")
#         return results


# # ---------------------------------------------------------------------------
# # OpenSearch implementation (kept mostly as-is, with small hardening)
# # ---------------------------------------------------------------------------

# class OpenSearchVectorStore(VectorStore):
#     """OpenSearch Serverless vector store."""

#     def __init__(self):
#         super().__init__()
#         try:
#             from opensearchpy import OpenSearch, RequestsHttpConnection  # type: ignore
#             from requests_aws4auth import AWS4Auth  # type: ignore
#             import boto3  # type: ignore
#         except ImportError as e:
#             raise ImportError("opensearch-py and requests-aws4auth are required") from e

#         self.OpenSearch = OpenSearch
#         self.RequestsHttpConnection = RequestsHttpConnection
#         self.AWS4Auth = AWS4Auth
#         self.boto3 = boto3

#         self.endpoint = get_env_var(
#             "OPENSEARCH_ENDPOINT",
#             self.config.get("vector_db", {}).get("opensearch", {}).get("endpoint"),
#         )
#         self.index_name = get_env_var(
#             "OPENSEARCH_INDEX_NAME",
#             self.config.get("vector_db", {}).get("opensearch", {}).get("index_name", "enterprise-rag-index"),
#         )

#         region = get_env_var("AWS_DEFAULT_REGION", "us-east-1")
#         session = self.boto3.Session()
#         credentials = session.get_credentials()
#         awsauth = self.AWS4Auth(
#             credentials.access_key,
#             credentials.secret_key,
#             region,
#             "aoss",
#             session_token=credentials.token,
#         )

#         self.client = self.OpenSearch(
#             hosts=[{"host": self.endpoint.replace("https://", ""), "port": 443}],
#             http_auth=awsauth,
#             use_ssl=True,
#             verify_certs=True,
#             connection_class=self.RequestsHttpConnection,
#         )

#         self._ensure_index_exists()

#     def _ensure_index_exists(self):
#         """Create index if it doesn't exist."""
#         if not self.client.indices.exists(index=self.index_name):
#             index_body = {
#                 "settings": {
#                     "index": {
#                         "knn": True,
#                         "knn.algo_param.ef_search": 100,
#                     }
#                 },
#                 "mappings": {
#                     "properties": {
#                         "text": {"type": "text"},
#                         "embedding": {
#                             "type": "knn_vector",
#                             "dimension": 1536,
#                         },
#                         "metadata": {"type": "object"},
#                     }
#                 },
#             }
#             self.client.indices.create(index=self.index_name, body=index_body)

#     def add_documents(self, chunks: List[Dict]):
#         """Add document chunks to OpenSearch."""
#         texts = [chunk["text"] for chunk in chunks if chunk.get("text")]
#         embeddings = self.embedder.embed_documents(texts)

#         for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
#             doc = {
#                 "text": chunk["text"],
#                 "embedding": embedding,
#                 "metadata": chunk.get("metadata", {}),
#                 "chunk_id": chunk.get("chunk_id", i),
#             }
#             self.client.index(index=self.index_name, body=doc, id=doc["chunk_id"])

#     def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
#         """Search for similar documents."""
#         top_k = top_k or self.top_k
#         query_embedding = self.embedder.embed_text(query)

#         search_body = {
#             "size": top_k,
#             "query": {
#                 "knn": {
#                     "embedding": {
#                         "vector": query_embedding,
#                         "k": top_k,
#                     }
#                 }
#             },
#         }

#         response = self.client.search(index=self.index_name, body=search_body)
#         results: List[Dict] = []

#         for hit in response["hits"]["hits"]:
#             # normalize score a bit
#             similarity = float(hit["_score"]) / 100.0
#             if similarity < self.similarity_threshold:
#                 continue
#             src = hit["_source"]
#             results.append(
#                 {
#                     "text": src["text"],
#                     "metadata": src.get("metadata", {}),
#                     "chunk_id": src.get("chunk_id"),
#                     "similarity": similarity,
#                 }
#             )

#         return results


# # ---------------------------------------------------------------------------
# # Factory
# # ---------------------------------------------------------------------------

# def get_vector_store():
#     """Factory function to get appropriate vector store."""
#     config = get_aws_config()
#     db_type = get_env_var("VECTOR_DB_TYPE", config.get("vector_db", {}).get("type", "faiss"))

#     if db_type == "faiss":
#         return FAISSVectorStore()
#     elif db_type == "opensearch":
#         return OpenSearchVectorStore()
#     elif db_type == "pinecone":
#         raise NotImplementedError("Pinecone implementation coming soon")
#     else:
#         raise ValueError(f"Unknown vector DB type: {db_type}")
