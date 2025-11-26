# Enterprise RAG System Specification

## 1. Overview
This project implements a production-ready Retrieval-Augmented Generation (RAG) system designed for enterprise use cases. It leverages AWS Bedrock for LLM capabilities (Claude 3 Sonnet) and Titan Embeddings, with a flexible vector store layer (FAISS/OpenSearch) and a modern web interface.

## 2. Architecture

### 2.1 High-Level Components
-   **Frontend**: A responsive, dark-mode web interface (HTML/CSS/JS) for user interaction.
-   **API Layer**: FastAPI-based REST API handling requests, ingestion, and static file serving.
-   **Orchestration**: `RAGPipeline` manages the flow of data between retrieval, generation, and validation.
-   **Ingestion**: `IngestionPipeline` processes documents (PDF, TXT, etc.), chunks them, and stores embeddings.
-   **Vector Store**: Abstraction layer supporting FAISS (local) and OpenSearch (serverless).
-   **LLM Integration**: AWS Bedrock integration for both embedding generation and text generation.

### 2.2 Data Flow
1.  **Ingestion**:
    -   User uploads/points to S3 documents.
    -   `DocumentProcessor` loads and cleans text.
    -   `TextSplitter` chunks text (hybrid strategy).
    -   `BedrockEmbeddings` generates vectors.
    -   `VectorStore` indexes vectors + metadata.

2.  **Query**:
    -   User submits query via UI.
    -   `QueryRewriter` expands query using LLM.
    -   `VectorStore` retrieves top-k relevant chunks (Cosine Similarity).
    -   `BedrockLLM` generates answer using Chain-of-Thought (CoT) and retrieved context.
    -   `QualityChecker` validates answer grounding and relevance using LLM.
    -   Response returned to UI with citations.

## 3. Key Features

### 3.1 Advanced RAG
-   **Query Rewriting**: Transforms ambiguous user queries into precise search terms.
-   **Chain-of-Thought**: LLM "thinks" before answering to improve logic and accuracy.
-   **LLM-based Validation**: A second LLM pass verifies if the answer is actually supported by the retrieved documents, reducing hallucinations.

### 3.2 Technical Stack
-   **Language**: Python 3.10+
-   **Framework**: FastAPI
-   **LLM**: Claude 3 Sonnet (AWS Bedrock)
-   **Embeddings**: Titan Text Embeddings v2
-   **Vector DB**: FAISS (Local), OpenSearch (Production)
-   **Frontend**: Vanilla JS/CSS (No build step required)

## 4. API Endpoints

### `POST /query`
-   **Input**: `{"question": str, "top_k": int}`
-   **Output**: JSON with answer, sources, confidence score, and validation details.

### `POST /ingest/s3`
-   **Input**: `prefix` (S3 folder path)
-   **Output**: Ingestion status and chunk count.

### `GET /health`
-   **Output**: System health status.

## 5. Configuration
Configuration is managed via `config/rag_config.yaml` and `.env`.

### Key Configs
-   `retrieval.similarity_threshold`: 0.2 (Filters irrelevant chunks)
-   `retrieval.top_k`: 5
-   `generation.model`: anthropic.claude-3-sonnet-20240229-v1:0
-   `generation.system_prompt`: Custom prompt for CoT.

## 6. Security
-   **AWS IAM**: Least privilege access for Bedrock and S3.
-   **Input Validation**: Pydantic models for all API inputs.
-   **Sanitization**: Basic input sanitization before LLM processing.

## 7. Future Improvements
-   **Reranking**: Implement cross-encoder reranking for better precision.
-   **Multi-modal**: Support for image/table extraction from PDFs.
-   **User Auth**: Integrate OAuth/Cognito for user management.
