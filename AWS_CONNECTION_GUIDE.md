# AWS Connection Guide - Step by Step

This guide will walk you through connecting your project to AWS so you can run the code.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] AWS Account (if not, create one at aws.amazon.com)
- [ ] AWS CLI installed (optional but helpful)
- [ ] Python 3.9+ installed
- [ ] Project dependencies installed (`pip install -r requirements.txt`)

---

## 🔧 Step 1: Create S3 Bucket (5 minutes)

### Option A: Using AWS Console (Web Interface)

1. **Go to S3 Console**
   - Visit: https://console.aws.amazon.com/s3/
   - Click "Create bucket"

2. **Configure Bucket**
   - **Bucket name**: `your-company-documents-rag` (must be globally unique)
   - **Region**: `us-east-1` (or your preferred region)
   - **Object Ownership**: ACLs disabled (recommended)
   - **Block Public Access**: Keep all settings enabled (for security)

3. **Enable Versioning** (Recommended)
   - Scroll to "Bucket Versioning"
   - Select "Enable"
   - This allows you to recover deleted documents

4. **Enable Encryption** (Recommended)
   - Scroll to "Default encryption"
   - Select "Enable"
   - Encryption type: "Server-side encryption with Amazon S3 managed keys (SSE-S3)"

5. **Create Bucket**
   - Click "Create bucket" at the bottom

### Option B: Using AWS CLI

```bash
# Create bucket
aws s3 mb s3://your-company-documents-rag --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket your-company-documents-rag \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-company-documents-rag \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**✅ Save your bucket name!** You'll need it for configuration.

---

## 🔧 Step 2: Request AWS Bedrock Access (10 minutes)

### 2.1 Go to Bedrock Console

1. Visit: https://console.aws.amazon.com/bedrock/
2. If this is your first time, you may see a welcome screen

### 2.2 Request Model Access

1. **Click "Model access"** in the left sidebar (or go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)

2. **Click "Edit"** or "Manage model access"

3. **Request Access to These Models:**
   
   **For Embeddings:**
   - ✅ **Amazon Titan Embeddings G1 - Text** (`amazon.titan-embed-text-v1`)
   - This is usually approved instantly
   
   **For Answer Generation:**
   - ✅ **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - ✅ **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`) - Optional but recommended
   - These may take a few minutes to hours for approval

4. **Click "Save changes"**

5. **Wait for Approval**
   - Titan Embeddings: Usually instant ✅
   - Claude models: Can take 5 minutes to 24 hours
   - You'll receive an email when approved

**💡 Tip:** While waiting, continue with Step 3 (IAM setup)

---

## 🔧 Step 3: Create IAM User and Get Credentials (5 minutes)

### 3.1 Create IAM User

1. **Go to IAM Console**
   - Visit: https://console.aws.amazon.com/iam/
   - Click "Users" in the left sidebar
   - Click "Create user"

2. **Set User Details**
   - **User name**: `rag-application-user` (or your preferred name)
   - Click "Next"

3. **Set Permissions** (We'll attach policies in next step)
   - Click "Next" (skip for now)

4. **Review and Create**
   - Click "Create user"

### 3.2 Attach Policies

1. **Click on the user** you just created (`rag-application-user`)

2. **Click "Add permissions"** → "Attach policies directly"

3. **Attach S3 Policy:**
   - Search for: `AmazonS3FullAccess`
   - ✅ Check the box
   - **OR** create a custom policy (more secure - see below)

4. **Create Custom Bedrock Policy:**
   - Click "Policies" in left sidebar
   - Click "Create policy"
   - Click "JSON" tab
   - Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
      ]
    }
  ]
}
```

   - Click "Next"
   - Policy name: `BedrockRAGAccess`
   - Description: "Allow access to Bedrock models for RAG application"
   - Click "Create policy"

5. **Attach Bedrock Policy to User:**
   - Go back to your user
   - Click "Add permissions" → "Attach policies directly"
   - Search for: `BedrockRAGAccess`
   - ✅ Check the box
   - Click "Add permissions"

### 3.3 Create Access Keys

1. **Go to your user** (`rag-application-user`)

2. **Click "Security credentials" tab**

3. **Scroll to "Access keys"**

4. **Click "Create access key"**

5. **Use case**: Select "Application running outside AWS"

6. **Click "Next"** → "Create access key"

7. **⚠️ IMPORTANT: Save these credentials!**
   - **Access Key ID**: Copy this
   - **Secret Access Key**: Copy this (you can only see it once!)
   - Click "Download .csv file" to save securely

**🔒 Keep these credentials secure! Never commit them to Git.**

---

## 🔧 Step 4: Configure Your Project (2 minutes)

### 4.1 Create .env File

Create a file named `.env` in your project root:

```bash
cd /Users/avdhootkulkarni/Desktop/RAG
touch .env
```

### 4.2 Add Your AWS Credentials

Open `.env` and add:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID_HERE
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY_HERE
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-company-documents-rag

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Vector Database (use FAISS for local development)
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index
```

**Replace:**
- `YOUR_ACCESS_KEY_ID_HERE` with your actual Access Key ID
- `YOUR_SECRET_ACCESS_KEY_HERE` with your actual Secret Access Key
- `your-company-documents-rag` with your actual S3 bucket name

### 4.3 Verify .env is Not Tracked

```bash
# This should output: .env
git check-ignore .env
```

---

## 🔧 Step 5: Test AWS Connection (1 minute)

Run the test script:

```bash
python scripts/test_aws_connection.py
```

**Expected Output:**
```
✅ S3 connection successful! Bucket: your-company-documents-rag
✅ Bedrock client initialized! Model: anthropic.claude-3-sonnet-20240229-v1:0
✅ Vector store initialized! Type: FAISSVectorStore
🎉 All connections successful!
```

**If you see errors:**
- **S3 Error**: Check bucket name and IAM permissions
- **Bedrock Error**: Verify model access is approved
- **Credentials Error**: Check .env file values

---

## 📤 Step 6: Upload Documents to S3

### What Files to Upload?

Upload your **company documents** that you want to query:

**Supported Formats:**
- ✅ PDF files (`.pdf`)
- ✅ Word documents (`.docx`)
- ✅ Text files (`.txt`)
- ✅ Markdown files (`.md`)

**What to Upload:**
- Company policies
- Product documentation
- Training materials
- FAQs
- Technical documentation
- Any documents you want to query

**What NOT to Upload:**
- ❌ Personal files
- ❌ Sensitive/confidential data (unless encrypted)
- ❌ Very large files (>100MB may be slow)

### How to Upload Documents

#### Option A: Using AWS Console (Easiest)

1. **Go to S3 Console**
   - Visit: https://console.aws.amazon.com/s3/
   - Click on your bucket: `your-company-documents-rag`

2. **Create Folder Structure**
   - Click "Create folder"
   - Name: `raw-documents`
   - Click "Create folder"

3. **Upload Files**
   - Navigate into `raw-documents/` folder
   - Click "Upload"
   - Click "Add files" or drag and drop
   - Select your documents
   - Click "Upload"

**Recommended Structure:**
```
your-company-documents-rag/
└── raw-documents/
    ├── company-policy.pdf
    ├── product-docs.docx
    ├── faq.txt
    └── training-materials.pdf
```

#### Option B: Using AWS CLI

```bash
# Upload a single file
aws s3 cp document.pdf s3://your-company-documents-rag/raw-documents/

# Upload entire directory
aws s3 cp ./my-documents/ s3://your-company-documents-rag/raw-documents/ --recursive

# Upload with specific name
aws s3 cp local-file.pdf s3://your-company-documents-rag/raw-documents/company-policy.pdf
```

#### Option C: Using Python Script

```python
from src.ingestion.s3_document_loader import S3DocumentLoader

loader = S3DocumentLoader()

# Upload a file
with open('document.pdf', 'rb') as f:
    file_content = f.read()
    loader.upload_document(file_content, 'raw-documents/document.pdf')
```

#### Option D: Using API Endpoint

Once your app is running:

```bash
# Start the app
python app.py

# In another terminal, upload via API
curl -X POST "http://localhost:8000/ingest/file?upload_to_s3=true" \
  -F "file=@document.pdf"
```

---

## 🚀 Step 7: Ingest Documents into Vector Database

After uploading documents to S3, ingest them:

### Option A: Using Python

```python
from src.ingestion.pipeline import IngestionPipeline

# Initialize pipeline
pipeline = IngestionPipeline()

# Ingest all documents from S3
result = pipeline.ingest_from_s3(prefix="raw-documents/")

print(f"Processed {result['documents_processed']} documents")
print(f"Created {result['chunks_created']} chunks")
```

### Option B: Using API

```bash
# Start the app
python app.py

# Ingest from S3
curl -X POST "http://localhost:8000/ingest/s3?prefix=raw-documents/"
```

### Option C: Using Script

```bash
python -c "
from src.ingestion.pipeline import IngestionPipeline
pipeline = IngestionPipeline()
result = pipeline.ingest_from_s3(prefix='raw-documents/')
print(f'✅ Processed {result[\"documents_processed\"]} documents')
print(f'✅ Created {result[\"chunks_created\"]} chunks')
"
```

---

## ✅ Step 8: Test the Complete System

### 8.1 Start the Application

```bash
python app.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 8.2 Test Query

```bash
# In another terminal
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the company policy?"}'
```

Or use Python:

```python
from src.rag_pipeline import RAGPipeline

rag = RAGPipeline()
result = rag.query("What is the company policy?")
print(result['answer'])
```

---

## 📋 Complete Setup Checklist

- [ ] S3 bucket created
- [ ] S3 bucket versioning enabled
- [ ] S3 bucket encryption enabled
- [ ] Bedrock model access requested
- [ ] Bedrock access approved (check email)
- [ ] IAM user created
- [ ] IAM policies attached (S3 + Bedrock)
- [ ] Access keys created and saved
- [ ] .env file created with credentials
- [ ] AWS connection tested successfully
- [ ] Documents uploaded to S3
- [ ] Documents ingested into vector database
- [ ] Application tested with query

---

## 🆘 Troubleshooting

### "Access Denied" to S3
- Check bucket name in .env matches actual bucket
- Verify IAM user has S3 permissions
- Check bucket region matches AWS_DEFAULT_REGION

### "Access Denied" to Bedrock
- Verify model access is approved in Bedrock console
- Check IAM policy includes correct model ARNs
- Wait for approval email (can take time)

### "Bucket not found"
- Verify bucket name is correct
- Check bucket exists in the correct region
- Ensure bucket name is globally unique

### "Invalid credentials"
- Verify Access Key ID and Secret are correct
- Check for extra spaces in .env file
- Ensure .env file is in project root

### Documents not found
- Check S3 prefix matches (should be `raw-documents/`)
- Verify files are actually uploaded to S3
- Check file format is supported (PDF, DOCX, TXT, MD)

---

## 🎯 Quick Reference

**S3 Bucket Structure:**
```
your-company-documents-rag/
└── raw-documents/          ← Upload your files here
    ├── document1.pdf
    ├── document2.docx
    └── document3.txt
```

**Required .env Variables:**
```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

**Test Commands:**
```bash
# Test connection
python scripts/test_aws_connection.py

# Ingest documents
python -c "from src.ingestion.pipeline import IngestionPipeline; IngestionPipeline().ingest_from_s3(prefix='raw-documents/')"

# Query documents
python -c "from src.rag_pipeline import RAGPipeline; print(RAGPipeline().query('Your question')['answer'])"
```

---

**You're all set!** 🎉 Now you can upload documents and start querying your knowledge base!

