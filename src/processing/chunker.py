"""Document chunking strategies for RAG."""
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from src.utils.config_loader import get_rag_config
from src.processing.text_cleaner import TextCleaner


class DocumentChunker:
    """Chunk documents using various strategies."""
    
    def __init__(self):
        self.config = get_rag_config()
        chunk_config = self.config.get("document_processing", {}).get("chunking", {})
        self.chunk_size = chunk_config.get("chunk_size", 1000)
        self.chunk_overlap = chunk_config.get("chunk_overlap", 200)
        self.strategy = chunk_config.get("strategy", "traditional")
        self.text_cleaner = TextCleaner()
    
    def chunk_document(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Chunk a document based on configured strategy."""
        # Clean text first
        cleaned_text = self.text_cleaner.clean_text(text)
        
        if self.strategy == "traditional":
            return self._traditional_chunking(cleaned_text, metadata)
        elif self.strategy == "logical":
            return self._logical_chunking(cleaned_text, metadata)
        elif self.strategy == "hybrid":
            return self._hybrid_chunking(cleaned_text, metadata)
        else:
            return self._traditional_chunking(cleaned_text, metadata)
    
    def _traditional_chunking(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Traditional fixed-size chunking with overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                'text': chunk,
                'chunk_id': i,
                'metadata': metadata or {},
                'chunk_type': 'traditional'
            })
        
        return result
    
    def _logical_chunking(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Logical/semantic chunking that preserves context."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'chunk_id': chunk_id,
                    'metadata': metadata or {},
                    'chunk_type': 'logical'
                })
                current_chunk = para
                chunk_id += 1
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_id': chunk_id,
                'metadata': metadata or {},
                'chunk_type': 'logical'
            })
        
        return chunks
    
    def _hybrid_chunking(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Hybrid approach: logical first, then traditional if needed."""
        # First try logical chunking
        logical_chunks = self._logical_chunking(text, metadata)
        
        # If any chunk is too large, split it traditionally
        final_chunks = []
        for chunk in logical_chunks:
            if len(chunk['text']) > self.chunk_size * 1.5:
                # Split large logical chunks
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                sub_chunks = splitter.split_text(chunk['text'])
                for i, sub_chunk in enumerate(sub_chunks):
                    final_chunks.append({
                        'text': sub_chunk,
                        'chunk_id': f"{chunk['chunk_id']}_{i}",
                        'metadata': chunk['metadata'],
                        'chunk_type': 'hybrid'
                    })
            else:
                final_chunks.append(chunk)
        
        return final_chunks

