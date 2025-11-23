# Enterprise Document QA and Search Assistant - Project Summary

## 🎯 Project Overview

This is a **production-ready Enterprise Document QA and Search Assistant** built with AWS, Generative AI, and advanced RAG (Retrieval-Augmented Generation) techniques. The system enables organizations to securely ingest, index, and query their document knowledge base with accurate, source-cited answers.

## 🏗️ Architecture

### AWS Components Integration

1. **Amazon S3**
   - Document storage and ingestion
   - Organized bucket structure (raw-documents, processed, metadata)
   - Secure access via IAM policies

2. **AWS Bedrock**
   - **Claude 3 Sonnet**: Primary LLM for answer generation
   - **Claude 3 Haiku**: Fast generation for simple tasks
   - **Amazon Titan Embeddings**: Vector embeddings for semantic search

3. **Vector Database Options**
   - **Amazon OpenSearch Serverless**: Production vector store
   - **Pinecone**: Managed vector database alternative
   - **FAISS**: Local development option

4. **Optional AWS Services**
   - **Lambda**: Serverless document processing
   - **API Gateway**: REST API endpoints
   - **IAM**: Secure access control

### Core RAG Pipeline

```
Document Ingestion → Processing → Chunking → Embedding → Vector Store
                                                              ↓
User Query → Query Rewriting → Retrieval → Generation → Validation → Response
```

## 📁 Project Structure

```
enterprise-rag/
├── src/
│   ├── ingestion/              # S3 document loading and processing
│   │   ├── s3_document_loader.py
│   │   ├── document_processor.py
│   │   └── pipeline.py
│   ├── processing/             # Text cleaning and chunking
│   │   ├── text_cleaner.py
│   │   └── chunker.py
│   ├── embedding/              # Vector embeddings
│   │   └── bedrock_embeddings.py
│   ├── retrieval/              # Semantic search
│   │   └── vector_store.py
│   ├── generation/             # LLM answer generation
│   │   └── bedrock_llm.py
│   ├── validation/             # Quality checks
│   │   └── quality_checker.py
│   ├── utils/                  # Configuration and AWS clients
│   │   ├── config_loader.py
│   │   └── aws_client.py
│   └── rag_pipeline.py         # Main pipeline orchestrator
├── config/
│   ├── aws_config.yaml         # AWS service configuration
│   └── rag_config.yaml         # RAG pipeline settings
├── scripts/
│   ├── setup.py                # Project setup script
│   └── test_aws_connection.py  # AWS connection testing
├── examples/
│   └── usage_example.py        # Usage examples
├── app.py                      # FastAPI application
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── AWS_SETUP.md               # Detailed AWS setup guide
└── PROJECT_SUMMARY.md         # This file
```

## 🔑 Key Features

### 1. Document Ingestion
- ✅ S3 integration for document storage
- ✅ Support for PDF, DOCX, TXT, MD formats
- ✅ Automatic document processing and chunking
- ✅ Metadata extraction and preservation

### 2. Advanced Chunking Strategies
- **Traditional**: Fixed-size chunks with overlap
- **Logical**: Semantic-aware chunking preserving context
- **Hybrid**: Combination of both approaches

### 3. Semantic Search
- Vector embeddings using AWS Bedrock Titan
- Multiple vector database backends
- Configurable similarity thresholds
- Top-K retrieval with relevance scoring

### 4. Answer Generation
- AWS Bedrock Claude 3 for high-quality responses
- Source citation and attribution
- Context-aware generation
- Configurable temperature and token limits

### 5. Quality Validation
- **Relevancy Check**: Verify retrieved documents are relevant
- **Grounding Check**: Ensure answers are based on context
- **Hallucination Detection**: Prevent fabricated information
- **Confidence Scoring**: Overall quality metrics

### 6. REST API
- FastAPI-based endpoints
- Document upload and ingestion
- Query interface
- Health checks and monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- AWS Account with appropriate permissions
- AWS CLI configured

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS**
   - Follow `AWS_SETUP.md` for detailed instructions
   - Set up S3 bucket, Bedrock access, and vector database
   - Configure `.env` file with credentials

3. **Test Connections**
   ```bash
   python scripts/test_aws_connection.py
   ```

4. **Run Setup**
   ```bash
   python scripts/setup.py
   ```

5. **Start Application**
   ```bash
   python app.py
   ```

6. **Ingest Documents**
   ```python
   from src.ingestion.pipeline import IngestionPipeline
   pipeline = IngestionPipeline()
   pipeline.ingest_from_s3(prefix="raw-documents/")
   ```

7. **Query Documents**
   ```python
   from src.rag_pipeline import RAGPipeline
   rag = RAGPipeline()
   result = rag.query("What is our refund policy?")
   ```

## 📊 API Endpoints

### Query Documents
```bash
POST /query
{
  "question": "What is the company policy?",
  "top_k": 5
}
```

### Ingest from S3
```bash
POST /ingest/s3?s3_key=raw-documents/example.pdf
```

### Upload and Ingest File
```bash
POST /ingest/file
Content-Type: multipart/form-data
file: [document file]
```

## 🔒 Security Features

- IAM-based access control
- Encrypted S3 storage (SSE-S3 or SSE-KMS)
- Secure credential management via environment variables
- Document access logging
- Least privilege IAM policies

## 📈 Performance Considerations

- **Embedding Batch Size**: Configurable (default: 32)
- **Chunk Size**: Optimizable (default: 1000 tokens)
- **Retrieval Top-K**: Configurable (default: 5)
- **Similarity Threshold**: Filter low-relevance results (default: 0.7)

## 🔧 Configuration

### AWS Configuration (`config/aws_config.yaml`)
- S3 bucket settings
- Bedrock model selection
- Vector database configuration
- Region and credentials

### RAG Configuration (`config/rag_config.yaml`)
- Chunking strategy and parameters
- Retrieval settings
- Generation parameters
- Validation thresholds

### Environment Variables (`.env`)
- AWS credentials
- Service endpoints
- Feature flags

## 🧪 Testing

### Connection Testing
```bash
python scripts/test_aws_connection.py
```

### Usage Examples
```bash
python examples/usage_example.py
```

## 📚 Documentation

- **README.md**: Main project documentation
- **AWS_SETUP.md**: Comprehensive AWS setup guide
- **spec.md**: Original RAG pipeline specification
- **PROJECT_SUMMARY.md**: This file

## 🎓 Based On

This project is inspired by and builds upon:
- [Complex RAG Guide](https://github.com/FareedKhan-dev/complex-RAG-guide)
- Advanced RAG techniques including:
  - Query rewriting
  - Chain-of-thought reasoning
  - Planning and execution
  - Multi-layer validation
  - RAGAS evaluation framework

## 🔮 Future Enhancements

- [ ] Query planning and execution system
- [ ] Chain-of-thought reasoning for complex queries
- [ ] RAGAS evaluation integration
- [ ] Multi-modal support (images, tables)
- [ ] Real-time document updates
- [ ] User feedback integration
- [ ] Advanced re-ranking strategies
- [ ] Conversational RAG with memory
- [ ] Pinecone integration
- [ ] Lambda-based async processing

## 💡 Usage Tips

1. **Start with FAISS** for local development, then migrate to OpenSearch/Pinecone for production
2. **Test chunking strategies** to find optimal size for your documents
3. **Monitor confidence scores** to identify low-quality responses
4. **Use validation results** to improve retrieval and generation
5. **Enable S3 versioning** for document recovery
6. **Set up CloudTrail** for audit logging

## 🆘 Troubleshooting

See `AWS_SETUP.md` for common issues and solutions related to:
- AWS connection problems
- Bedrock model access
- Vector database setup
- IAM permissions

## 📄 License

Apache 2.0

---

**Built with ❤️ using AWS, LangChain, and advanced RAG techniques**

