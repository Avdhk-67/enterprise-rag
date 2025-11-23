# AWS Components - Essential vs Optional

## 🔴 **ESSENTIAL AWS Components** (Required for System to Work)

### 1. **Amazon S3** ✅ **MANDATORY**
**Purpose:** Document storage and retrieval

**Why Essential:**
- Used in: `src/ingestion/s3_document_loader.py`
- Functions: Upload, download, list, and manage documents
- **Cannot be replaced** - core to document ingestion pipeline

**What it does:**
- Stores original documents (PDFs, DOCX, TXT)
- Organized structure: `raw-documents/`, `processed/`, `metadata/`
- Secure document access via IAM

**Code Usage:**
```python
# Used throughout ingestion pipeline
s3_client.get_object()      # Download documents
s3_client.put_object()      # Upload documents
s3_client.list_objects_v2() # List documents
```

**Setup Required:**
- Create S3 bucket
- Configure bucket policies
- Enable encryption (recommended)

---

### 2. **AWS Bedrock** ✅ **MANDATORY**
**Purpose:** AI/ML models for embeddings and text generation

**Why Essential:**
- Used in: `src/embedding/bedrock_embeddings.py` and `src/generation/bedrock_llm.py`
- **Cannot be replaced** - core to RAG functionality

**What it provides:**

#### A. **Amazon Titan Embeddings** (Required)
- Model: `amazon.titan-embed-text-v1`
- Purpose: Convert text to 1536-dimensional vectors
- Used for: Document embeddings and query embeddings
- **Essential for:** Vector search functionality

#### B. **Claude 3 Sonnet** (Required)
- Model: `anthropic.claude-3-sonnet-20240229-v1:0`
- Purpose: Generate answers from retrieved context
- Used for: Answer generation in RAG pipeline
- **Essential for:** AI-powered Q&A

**Code Usage:**
```python
# Embeddings
bedrock_client.invoke_model(
    modelId="amazon.titan-embed-text-v1",
    body={"inputText": text}
)

# LLM Generation
bedrock_client.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    body={"messages": [...]}
)
```

**Setup Required:**
- Request model access in Bedrock console
- Approve access to Titan Embeddings
- Approve access to Claude 3 Sonnet
- Configure IAM permissions

---

### 3. **IAM (Identity and Access Management)** ✅ **MANDATORY**
**Purpose:** Security and access control

**Why Essential:**
- Required for: Authenticating to S3 and Bedrock
- Manages: User credentials, roles, and policies
- **Cannot be replaced** - AWS security requirement

**What it does:**
- Creates IAM user with access keys
- Attaches policies for S3 and Bedrock access
- Manages permissions (least privilege)

**Setup Required:**
- Create IAM user
- Generate access keys (Access Key ID + Secret)
- Attach S3 and Bedrock policies

---

## 🟡 **OPTIONAL AWS Components** (Can Use Alternatives)

### 4. **Amazon OpenSearch Serverless** ⚠️ **OPTIONAL**
**Purpose:** Vector database for production

**Why Optional:**
- Only used if: `VECTOR_DB_TYPE=opensearch` in config
- Alternative: FAISS (local, free, no AWS needed)
- **Can be replaced** - FAISS works for development/testing

**What it does:**
- Stores vector embeddings in cloud
- Provides managed vector search
- Scalable for production workloads

**When to Use:**
- ✅ Production deployments
- ✅ Large-scale document collections
- ✅ Need for cloud-based persistence
- ✅ Multi-user access

**When NOT to Use:**
- ❌ Development/testing (use FAISS instead)
- ❌ Small document collections
- ❌ Single-user scenarios
- ❌ Cost-sensitive projects

**Code Usage:**
```python
# Only initialized if VECTOR_DB_TYPE=opensearch
if db_type == "opensearch":
    return OpenSearchVectorStore()
else:
    return FAISSVectorStore()  # Default
```

---

## 🟢 **NOT USED** (Mentioned in Docs but Not in Code)

### 5. **AWS Lambda** ❌ **NOT IMPLEMENTED**
**Status:** Mentioned in documentation but not in code

**Potential Use:**
- Serverless document processing
- Async ingestion pipeline
- Event-driven architecture

**Current Implementation:**
- Uses FastAPI server (not Lambda)
- Synchronous processing
- Can be added as future enhancement

---

### 6. **API Gateway** ❌ **NOT IMPLEMENTED**
**Status:** Mentioned in documentation but not in code

**Potential Use:**
- Managed REST API endpoints
- Request throttling and caching
- API versioning

**Current Implementation:**
- Uses FastAPI directly (not API Gateway)
- Runs on local server or EC2
- Can be added as future enhancement

---

## 📊 Summary Table

| AWS Component | Status | Required? | Used For | Alternative |
|--------------|--------|-----------|----------|-------------|
| **S3** | ✅ Implemented | **YES** | Document storage | None (essential) |
| **Bedrock (Titan)** | ✅ Implemented | **YES** | Embeddings | None (essential) |
| **Bedrock (Claude)** | ✅ Implemented | **YES** | Answer generation | None (essential) |
| **IAM** | ✅ Implemented | **YES** | Authentication | None (essential) |
| **OpenSearch** | ✅ Implemented | **NO** | Vector database | FAISS (local) |
| **Lambda** | ❌ Not used | **NO** | Serverless processing | FastAPI server |
| **API Gateway** | ❌ Not used | **NO** | API management | FastAPI directly |

---

## 🎯 Minimum AWS Setup (Essential Only)

To run the system, you **MUST** have:

1. ✅ **S3 Bucket** - For document storage
2. ✅ **Bedrock Access** - For Titan Embeddings + Claude 3
3. ✅ **IAM Credentials** - For authentication

**Total:** 3 AWS services/components

---

## 💰 Cost Breakdown

### Essential Components:
- **S3**: ~$0.023/GB/month + $0.005 per 1K requests
- **Bedrock Titan**: ~$0.0001 per 1K tokens
- **Bedrock Claude**: ~$0.003 per 1K input, $0.015 per 1K output tokens
- **IAM**: Free

### Optional Components:
- **OpenSearch Serverless**: ~$0.10 per OCU-hour (only if used)

---

## 🔧 Configuration Impact

### If you use FAISS (no OpenSearch):
```yaml
# config/aws_config.yaml
vector_db:
  type: faiss  # Uses local file, no AWS needed
```

**AWS Components Needed:** S3 + Bedrock + IAM (3 components)

### If you use OpenSearch:
```yaml
# config/aws_config.yaml
vector_db:
  type: opensearch  # Uses AWS service
```

**AWS Components Needed:** S3 + Bedrock + IAM + OpenSearch (4 components)

---

## 🚀 Quick Reference

**Minimum Setup:**
- S3 bucket ✅
- Bedrock model access ✅
- IAM user with credentials ✅
- **Total: 3 components**

**Production Setup:**
- Everything above +
- OpenSearch Serverless (optional) ⚠️
- **Total: 3-4 components**

---

## 📝 Code Evidence

### Essential Components in Code:

**S3 Usage:**
- `src/ingestion/s3_document_loader.py` - All S3 operations
- `src/ingestion/pipeline.py` - Uses S3 loader

**Bedrock Usage:**
- `src/embedding/bedrock_embeddings.py` - Titan embeddings
- `src/generation/bedrock_llm.py` - Claude generation
- `src/validation/quality_checker.py` - Uses Bedrock LLM

**IAM Usage:**
- `src/utils/aws_client.py` - All AWS client initialization
- Uses credentials for S3 and Bedrock access

**OpenSearch Usage:**
- `src/retrieval/vector_store.py` - Only if `VECTOR_DB_TYPE=opensearch`
- Default is FAISS (no AWS needed)

---

## ✅ Conclusion

**Essential AWS Components (3):**
1. Amazon S3
2. AWS Bedrock (Titan + Claude)
3. IAM

**Optional AWS Components (1):**
1. Amazon OpenSearch Serverless (can use FAISS instead)

**Total AWS Services Needed:** 3-4 (depending on vector DB choice)

