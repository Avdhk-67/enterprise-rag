# AWS Connection Steps - Complete Guide

## 🎯 Goal: Connect to AWS and Run Your Code

This guide walks you through connecting to AWS and preparing your S3 bucket with documents.

---

## 📋 **Step-by-Step AWS Setup**

### **STEP 1: Create S3 Bucket** (5 minutes)

#### Option A: Using AWS CLI
```bash
# Create bucket
aws s3 mb s3://your-company-documents-rag --region us-east-1

# Verify it was created
aws s3 ls | grep your-company-documents-rag
```

#### Option B: Using AWS Console
1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click **"Create bucket"**
3. **Bucket name**: `your-company-documents-rag` (must be globally unique)
4. **Region**: `us-east-1` (or your preferred region)
5. **Block Public Access**: Keep all settings enabled (recommended)
6. **Bucket Versioning**: Enable (recommended)
7. **Default encryption**: Enable (SSE-S3)
8. Click **"Create bucket"**

#### Create Folder Structure
```bash
# Using AWS CLI
aws s3 mkdir s3://your-company-documents-rag/raw-documents
aws s3 mkdir s3://your-company-documents-rag/processed
aws s3 mkdir s3://your-company-documents-rag/metadata

# Or create folders manually in S3 Console
```

---

### **STEP 2: Request Bedrock Model Access** (10 minutes)

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click **"Model access"** in the left sidebar
3. Click **"Edit"** or **"Request model access"**
4. Find and enable these models:
   - ✅ **Amazon Titan Embeddings G1 - Text v1** (`amazon.titan-embed-text-v1`)
   - ✅ **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - ✅ **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`) - Optional but recommended
5. Click **"Save changes"** or **"Request access"**

**Note:**
- Titan Embeddings: Usually approved instantly
- Claude models: May take a few minutes to hours (usually instant for most accounts)

**Check Status:**
- Go back to "Model access"
- Status should show "Access granted" (green checkmark)

---

### **STEP 3: Create IAM User and Get Credentials** (5 minutes)

#### 3a. Create IAM User

**Using AWS Console:**
1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Click **"Users"** → **"Create user"**
3. **User name**: `rag-application-user`
4. Click **"Next"**

#### 3b. Attach Policies

**Option 1: Attach Managed Policies (Easier)**
1. Click **"Attach policies directly"**
2. Search and select:
   - ✅ **AmazonS3FullAccess** (or create custom policy for specific bucket)
   - ✅ **AmazonBedrockFullAccess** (or create custom policy)
3. Click **"Next"** → **"Create user"**

**Option 2: Create Custom Policies (More Secure)**

**S3 Policy** (`s3-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-company-documents-rag",
        "arn:aws:s3:::your-company-documents-rag/*"
      ]
    }
  ]
}
```

**Bedrock Policy** (`bedrock-policy.json`):
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

**Apply custom policies:**
```bash
# Create S3 policy
aws iam create-policy \
  --policy-name RAGS3Access \
  --policy-document file://s3-policy.json

# Create Bedrock policy
aws iam create-policy \
  --policy-name RAGBedrockAccess \
  --policy-document file://bedrock-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name rag-application-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/RAGS3Access

aws iam attach-user-policy \
  --user-name rag-application-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/RAGBedrockAccess
```

#### 3c. Create Access Keys
1. Click on the user `rag-application-user`
2. Go to **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**
5. Choose **"Application running outside AWS"**
6. Click **"Next"** → **"Create access key"**
7. **IMPORTANT**: Copy both:
   - **Access key ID**
   - **Secret access key** (only shown once!)
8. Save these securely (you'll need them for `.env` file)

---

### **STEP 4: Configure Your Local Environment** (2 minutes)

#### 4a. Create `.env` File

In your project root (`/Users/avdhootkulkarni/Desktop/RAG/`), create `.env`:

```bash
# Navigate to project
cd /Users/avdhootkulkarni/Desktop/RAG

# Create .env file
cat > .env << 'EOF'
# AWS Configuration
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID_HERE
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY_HERE
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-company-documents-rag
S3_RAW_DOCUMENTS_PREFIX=raw-documents
S3_PROCESSED_PREFIX=processed

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Vector Database (using FAISS for local development)
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7
EOF
```

**Replace:**
- `YOUR_ACCESS_KEY_ID_HERE` → Your actual Access Key ID
- `YOUR_SECRET_ACCESS_KEY_HERE` → Your actual Secret Access Key
- `your-company-documents-rag` → Your actual bucket name

#### 4b. Update Config Files

Edit `config/aws_config.yaml`:
```yaml
aws:
  s3:
    bucket_name: your-company-documents-rag  # Update this
  # ... rest stays the same
```

---

### **STEP 5: Test AWS Connection** (1 minute)

```bash
# Run the test script
python scripts/test_aws_connection.py
```

**Expected Output:**
```
✅ S3 connection successful! Bucket: your-company-documents-rag
✅ Bedrock client initialized! Model: anthropic.claude-3-sonnet-20240229-v1:0
✅ Vector store initialized! Type: FAISSVectorStore
🎉 All connections successful!
```

**If you get errors:**
- **S3 Error**: Check bucket name and IAM permissions
- **Bedrock Error**: Verify model access is granted
- **Credentials Error**: Verify `.env` file has correct values

---

## 📁 **What Files to Upload to S3**

### **Supported File Formats:**
- ✅ **PDF** (`.pdf`) - Most common
- ✅ **Word Documents** (`.docx`)
- ✅ **Text Files** (`.txt`)
- ✅ **Markdown** (`.md`)

### **S3 Folder Structure:**

```
your-company-documents-rag/
└── raw-documents/          ← Upload your documents here
    ├── policy-document.pdf
    ├── employee-handbook.docx
    ├── product-specs.txt
    └── faq.md
```

### **What Documents to Upload:**

#### **Example Documents (for testing):**
1. **Company Policy Document** (PDF)
   - HR policies, refund policies, terms of service
   
2. **Product Documentation** (DOCX/TXT)
   - User manuals, feature descriptions, API docs
   
3. **FAQ Document** (TXT/MD)
   - Common questions and answers
   
4. **Internal Knowledge Base** (PDF/DOCX)
   - Procedures, guidelines, best practices

#### **Real-World Examples:**
- Employee handbooks
- Product documentation
- Customer support FAQs
- Technical specifications
- Company policies
- Training materials
- Research papers
- Legal documents (if appropriate)

### **How to Upload Documents:**

#### **Method 1: AWS Console (Easiest)**
1. Go to [S3 Console](https://s3.console.aws.amazon.com/)
2. Click on your bucket: `your-company-documents-rag`
3. Click on folder: `raw-documents/`
4. Click **"Upload"**
5. Click **"Add files"** or drag and drop
6. Select your PDF/DOCX/TXT files
7. Click **"Upload"**

#### **Method 2: AWS CLI**
```bash
# Upload a single file
aws s3 cp /path/to/document.pdf s3://your-company-documents-rag/raw-documents/

# Upload multiple files
aws s3 cp /path/to/documents/ s3://your-company-documents-rag/raw-documents/ --recursive

# Upload with specific name
aws s3 cp document.pdf s3://your-company-documents-rag/raw-documents/company-policy.pdf
```

#### **Method 3: Using Python Script**
```python
from src.ingestion.s3_document_loader import S3DocumentLoader

loader = S3DocumentLoader()

# Upload a file
with open('document.pdf', 'rb') as f:
    file_content = f.read()
    loader.upload_document(file_content, 'raw-documents/document.pdf')
```

#### **Method 4: Using API (After Starting App)**
```bash
# Start the app
python app.py

# In another terminal, upload via API
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@/path/to/document.pdf" \
  -F "upload_to_s3=true"
```

---

## 🚀 **Complete Setup Checklist**

- [ ] S3 bucket created
- [ ] S3 folder structure created (`raw-documents/`)
- [ ] Bedrock model access requested and approved
- [ ] IAM user created
- [ ] IAM policies attached (S3 + Bedrock)
- [ ] Access keys created and saved
- [ ] `.env` file created with credentials
- [ ] `config/aws_config.yaml` updated with bucket name
- [ ] Test connection: `python scripts/test_aws_connection.py` ✅
- [ ] Documents uploaded to S3 `raw-documents/` folder

---

## 📝 **Quick Test After Setup**

### 1. Test Connection
```bash
python scripts/test_aws_connection.py
```

### 2. List Documents in S3
```bash
aws s3 ls s3://your-company-documents-rag/raw-documents/
```

### 3. Ingest Documents
```python
from src.ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline()
result = pipeline.ingest_from_s3(prefix="raw-documents/")
print(f"Processed {result['documents_processed']} documents")
print(f"Created {result['chunks_created']} chunks")
```

### 4. Query Documents
```python
from src.rag_pipeline import RAGPipeline

rag = RAGPipeline()
result = rag.query("What is the refund policy?")
print(result['answer'])
```

---

## 🆘 **Troubleshooting**

### **"Access Denied" to S3**
- Check IAM user has S3 permissions
- Verify bucket name in `.env`
- Check bucket policy allows your IAM user

### **"Access Denied" to Bedrock**
- Verify model access is granted in Bedrock console
- Check IAM user has Bedrock permissions
- Wait a few minutes if you just requested access

### **"Bucket not found"**
- Verify bucket name is correct
- Check region matches (us-east-1)
- Ensure bucket exists in S3 console

### **"Invalid credentials"**
- Verify `.env` file has correct values
- Check for extra spaces in credentials
- Ensure credentials are from correct IAM user

---

## ✅ **You're Ready!**

Once all steps are complete:
1. ✅ AWS connected
2. ✅ Documents uploaded to S3
3. ✅ Ready to run the code!

**Next:** Run `python app.py` and start querying your documents! 🎉


