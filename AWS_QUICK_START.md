# AWS Quick Start Guide

This is a condensed guide for setting up AWS components. For detailed instructions, see [AWS_SETUP.md](./AWS_SETUP.md).

## 🚀 Quick Setup Checklist

### 1. S3 Bucket (5 minutes)

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
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'
```

**Update `.env`:**
```bash
S3_BUCKET_NAME=your-company-documents-rag
```

### 2. AWS Bedrock (10 minutes)

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" → "Edit"
3. Request access to:
   - ✅ Claude 3 Sonnet
   - ✅ Claude 3 Haiku  
   - ✅ Amazon Titan Embeddings
4. Wait for approval (usually instant for Titan, may take time for Claude)

**Update `.env`:**
```bash
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```

### 3. IAM User & Permissions (5 minutes)

```bash
# Create IAM user
aws iam create-user --user-name rag-application-user

# Create access key (SAVE THE OUTPUT!)
aws iam create-access-key --user-name rag-application-user

# Attach policies
aws iam attach-user-policy \
  --user-name rag-application-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create Bedrock policy
cat > bedrock-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ],
    "Resource": [
      "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
      "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
      "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
    ]
  }]
}
EOF

aws iam put-user-policy \
  --user-name rag-application-user \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json
```

**Update `.env` with access keys:**
```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### 4. Vector Database (Choose One)

#### Option A: FAISS (Local - No Setup)
```bash
# No setup needed! Just update .env:
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index
```

#### Option B: OpenSearch Serverless (15 minutes)
1. Go to [OpenSearch Service Console](https://console.aws.amazon.com/aos/)
2. Create collection: `rag-vector-collection`
3. Type: Vector search
4. Note the endpoint URL

**Update `.env`:**
```bash
VECTOR_DB_TYPE=opensearch
OPENSEARCH_ENDPOINT=https://your-endpoint.us-east-1.aoss.amazonaws.com
OPENSEARCH_INDEX_NAME=enterprise-rag-index
```

#### Option C: Pinecone (10 minutes)
1. Sign up at [pinecone.io](https://www.pinecone.io)
2. Create index: `enterprise-rag`
3. Dimensions: 1536
4. Get API key from dashboard

**Update `.env`:**
```bash
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=enterprise-rag
```

## ✅ Verify Setup

```bash
# Test all connections
python scripts/test_aws_connection.py
```

Expected output:
```
✅ S3 connection successful!
✅ Bedrock client initialized!
✅ Vector store initialized!
🎉 All connections successful!
```

## 📝 Complete .env Template

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1

# S3
S3_BUCKET_NAME=your-company-documents-rag

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Vector DB (choose one)
VECTOR_DB_TYPE=faiss  # or opensearch or pinecone
FAISS_INDEX_PATH=./data/faiss_index

# Or for OpenSearch:
# OPENSEARCH_ENDPOINT=https://your-endpoint.us-east-1.aoss.amazonaws.com
# OPENSEARCH_INDEX_NAME=enterprise-rag-index

# Or for Pinecone:
# PINECONE_API_KEY=your_api_key
# PINECONE_ENVIRONMENT=us-east-1-aws
# PINECONE_INDEX_NAME=enterprise-rag
```

## 🎯 Next Steps

1. ✅ Run setup: `python scripts/setup.py`
2. ✅ Test connections: `python scripts/test_aws_connection.py`
3. ✅ Upload documents to S3: `aws s3 cp document.pdf s3://your-bucket/raw-documents/`
4. ✅ Ingest documents: Use API or `python examples/usage_example.py`
5. ✅ Start application: `python app.py`
6. ✅ Query documents: `POST http://localhost:8000/query`

## 🆘 Common Issues

**"Access Denied" to Bedrock:**
- Make sure you requested model access in Bedrock console
- Wait for approval (can take a few minutes to hours)

**"Bucket not found":**
- Check bucket name in `.env`
- Verify bucket exists: `aws s3 ls`

**"Invalid credentials":**
- Verify access keys in `.env`
- Check IAM user has correct policies attached

**Vector DB connection failed:**
- For OpenSearch: Check endpoint URL and IAM permissions
- For Pinecone: Verify API key and index name
- For FAISS: Ensure `data/` directory exists

## 💰 Estimated Costs (Monthly)

- **S3**: ~$0.023/GB storage + $0.005 per 1K requests
- **Bedrock Claude 3 Sonnet**: ~$0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Bedrock Titan Embeddings**: ~$0.0001 per 1K tokens
- **OpenSearch Serverless**: ~$0.10 per OCU-hour
- **Pinecone**: Free tier available, then ~$70/month

For small-medium enterprise: **~$50-200/month** depending on usage.

---

**Need help?** See [AWS_SETUP.md](./AWS_SETUP.md) for detailed instructions.

