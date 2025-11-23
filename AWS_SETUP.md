# AWS Setup Guide

This guide walks you through setting up all AWS components required for the Enterprise Document QA and Search Assistant.

## 📋 Prerequisites

- AWS Account
- AWS CLI installed and configured
- Appropriate IAM permissions

## 🔧 Step-by-Step AWS Setup

### 1. S3 Bucket Setup

#### Create S3 Bucket for Documents

```bash
# Using AWS CLI
aws s3 mb s3://your-company-documents-rag --region us-east-1

# Or using AWS Console:
# 1. Go to S3 Console
# 2. Click "Create bucket"
# 3. Name: your-company-documents-rag
# 4. Region: Choose your preferred region
# 5. Enable versioning (recommended)
# 6. Enable encryption (SSE-S3 or SSE-KMS)
```

#### S3 Bucket Structure

```
your-company-documents-rag/
├── raw-documents/          # Original uploaded documents
│   ├── pdfs/
│   ├── docs/
│   └── txts/
├── processed/              # Processed and chunked documents
└── metadata/               # Document metadata and indexes
```

#### Create S3 Bucket Policy

Create a policy file `s3-bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDocumentUpload",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_IAM_USER"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-company-documents-rag",
        "arn:aws:s3:::your-company-documents-rag/*"
      ]
    }
  ]
}
```

Apply the policy:
```bash
aws s3api put-bucket-policy --bucket your-company-documents-rag --policy file://s3-bucket-policy.json
```

### 2. AWS Bedrock Setup

#### Enable Bedrock Access

1. Go to AWS Bedrock Console
2. Navigate to "Model access" in the left sidebar
3. Request access to models:
   - **Claude 3 Sonnet** (for generation)
   - **Claude 3 Haiku** (for faster tasks)
   - **Amazon Titan Embeddings** (for embeddings)

#### Configure Bedrock IAM Policy

Create IAM policy `bedrock-policy.json`:

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

Attach to your IAM user/role:
```bash
aws iam put-user-policy --user-name YOUR_IAM_USER --policy-name BedrockAccess --policy-document file://bedrock-policy.json
```

### 3. Vector Database Setup

#### Option A: Amazon OpenSearch Serverless

1. Go to Amazon OpenSearch Service Console
2. Create a new collection:
   - Name: `rag-vector-collection`
   - Type: Vector search
   - Capacity: Choose based on your needs
3. Note the collection endpoint

#### Option B: Pinecone (Managed Service)

1. Sign up at [pinecone.io](https://www.pinecone.io)
2. Create a new index:
   - Name: `enterprise-rag`
   - Dimensions: 1536 (for Titan embeddings) or 1024 (for other models)
   - Metric: cosine
3. Get your API key from the dashboard

#### Option C: Local FAISS (Development)

No setup needed - works locally for development/testing.

### 4. IAM User and Credentials Setup

#### Create IAM User

```bash
# Create IAM user
aws iam create-user --user-name rag-application-user

# Create access key
aws iam create-access-key --user-name rag-application-user
```

**Save the Access Key ID and Secret Access Key securely!**

#### Attach Policies

```bash
# Attach S3 full access (or create custom policy)
aws iam attach-user-policy --user-name rag-application-user --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach Bedrock policy (created earlier)
aws iam attach-user-policy --user-name rag-application-user --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAccess
```

### 5. AWS Credentials Configuration

#### Option 1: AWS Credentials File

Edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
region = us-east-1
```

#### Option 2: Environment Variables

Add to your `.env` file:

```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: IAM Role (for EC2/Lambda)

If running on EC2 or Lambda, use IAM roles instead of access keys.

### 6. Optional: Lambda Function Setup (for Async Processing)

#### Create Lambda Function

1. Go to Lambda Console
2. Create function:
   - Name: `rag-document-processor`
   - Runtime: Python 3.11
   - Handler: `lambda_function.lambda_handler`
3. Add environment variables:
   - `S3_BUCKET`: your-company-documents-rag
   - `VECTOR_DB_TYPE`: opensearch/pinecone
4. Set timeout: 5 minutes
5. Increase memory: 1024 MB

#### Create S3 Event Trigger

```bash
aws lambda add-permission \
  --function-name rag-document-processor \
  --principal s3.amazonaws.com \
  --statement-id s3-trigger \
  --action "lambda:InvokeFunction" \
  --source-arn arn:aws:s3:::your-company-documents-rag
```

### 7. Optional: API Gateway Setup

1. Go to API Gateway Console
2. Create REST API
3. Create resources and methods
4. Deploy API
5. Note the API endpoint

## 🔐 Security Best Practices

1. **Use IAM Roles** instead of access keys when possible (EC2, Lambda, ECS)
2. **Enable S3 Bucket Encryption** (SSE-S3 or SSE-KMS)
3. **Enable S3 Versioning** for document recovery
4. **Use VPC Endpoints** for private S3 access
5. **Enable CloudTrail** for audit logging
6. **Rotate Access Keys** regularly
7. **Use Least Privilege** IAM policies

## 📝 Configuration Checklist

- [ ] S3 bucket created and configured
- [ ] S3 bucket policy applied
- [ ] Bedrock model access requested and approved
- [ ] Bedrock IAM policy attached
- [ ] Vector database set up (OpenSearch/Pinecone/FAISS)
- [ ] IAM user created with appropriate permissions
- [ ] AWS credentials configured
- [ ] Environment variables set in `.env`
- [ ] Lambda function created (optional)
- [ ] API Gateway configured (optional)

## 🧪 Testing AWS Connection

Run the test script:

```bash
python scripts/test_aws_connection.py
```

This will verify:
- S3 bucket access
- Bedrock model access
- Vector database connection
- IAM permissions

## 💰 Cost Estimation

**Estimated Monthly Costs (for small-medium enterprise):**

- **S3 Storage**: ~$0.023/GB/month
- **S3 Requests**: ~$0.005 per 1000 requests
- **Bedrock (Claude 3 Sonnet)**: ~$0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Bedrock (Titan Embeddings)**: ~$0.0001 per 1K tokens
- **OpenSearch Serverless**: ~$0.10 per OCU-hour
- **Pinecone**: Free tier available, then ~$70/month for starter

## 🆘 Troubleshooting

### Common Issues

1. **Access Denied to Bedrock**
   - Ensure model access is requested and approved
   - Check IAM policy includes correct model ARNs

2. **S3 Access Denied**
   - Verify bucket policy allows your IAM user
   - Check IAM user has S3 permissions

3. **Vector Database Connection Failed**
   - Verify endpoint URL is correct
   - Check network security groups (for OpenSearch)
   - Verify API keys (for Pinecone)

4. **Region Mismatch**
   - Ensure all services are in the same region
   - Update region in configuration files

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [OpenSearch Serverless Guide](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

