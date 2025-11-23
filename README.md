# Enterprise Document QA and Search Assistant

A production-ready RAG (Retrieval-Augmented Generation) system for enterprise document question-answering and search, built with AWS, Generative AI, and advanced RAG techniques.

## 🎯 Project Overview

This application enables organizations to:
- Securely ingest and index organizational documents from AWS S3
- Ask complex questions and get accurate, source-cited answers
- Search across company knowledge base with semantic understanding
- Reduce hallucinations through multi-layer validation
- Handle complex, multi-step reasoning queries

## 🏗️ Architecture

### AWS Components
- **S3**: Document storage and ingestion
- **AWS Bedrock**: LLM and embedding models (Claude, Titan)
- **Amazon OpenSearch Serverless** or **Pinecone**: Vector database for embeddings
- **IAM**: Secure access control
- **Lambda** (optional): Serverless document processing
- **API Gateway** (optional): REST API endpoints

### Core Components
1. **Document Ingestion Pipeline**: S3 → Processing → Vector Store
2. **RAG Pipeline**: Query → Retrieval → Generation → Validation
3. **Query Processing**: Query rewriting, CoT reasoning, planning
4. **Validation Layer**: Relevancy checks, grounding, hallucination prevention

## 📋 Prerequisites

- Python 3.9+
- AWS Account with appropriate permissions
- AWS CLI configured
- boto3 access to S3, Bedrock, and vector database

## 🚀 Quick Start

### 1. AWS Setup

See [AWS_SETUP.md](./AWS_SETUP.md) for detailed AWS configuration instructions.

**Quick AWS Setup Checklist:**
- [ ] Create S3 bucket for documents
- [ ] Set up AWS Bedrock access
- [ ] Configure IAM roles and policies
- [ ] Set up vector database (OpenSearch/Pinecone)
- [ ] Configure AWS credentials

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

### 4. Run Document Ingestion

```bash
python src/ingestion/document_processor.py
```

### 5. Start the Application

```bash
python app.py
```

## 📁 Project Structure

```
enterprise-rag/
├── src/
│   ├── ingestion/           # Document ingestion from S3
│   ├── processing/          # Document cleaning and chunking
│   ├── embedding/           # Vector embeddings
│   ├── retrieval/           # Semantic search
│   ├── generation/          # LLM answer generation
│   ├── validation/          # Quality checks
│   ├── planning/            # Query planning and execution
│   └── utils/               # Helper functions
├── config/                  # Configuration files
├── data/                    # Local data storage
├── tests/                   # Test files
├── app.py                   # Main application
├── requirements.txt         # Python dependencies
├── AWS_SETUP.md            # AWS configuration guide
└── README.md               # This file
```

## 🔧 Configuration

Key configuration files:
- `config/aws_config.yaml`: AWS service configuration
- `config/rag_config.yaml`: RAG pipeline settings
- `.env`: Environment variables (AWS credentials, API keys)

## 📚 Features

- ✅ Secure document ingestion from S3
- ✅ Advanced chunking strategies (traditional + logical)
- ✅ Semantic search with vector embeddings
- ✅ Complex query handling with CoT reasoning
- ✅ Multi-layer hallucination prevention
- ✅ Source citation and confidence scoring
- ✅ Query planning and execution
- ✅ RAGAS evaluation framework

## 🔒 Security

- IAM-based access control
- Encrypted S3 storage
- Secure credential management
- Document access logging

## 📊 Evaluation

Use RAGAS framework for evaluation:
```bash
python src/evaluation/evaluate_rag.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

Apache 2.0

## 🔗 References

- [Complex RAG Guide](https://github.com/FareedKhan-dev/complex-RAG-guide)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain Documentation](https://python.langchain.com/)

