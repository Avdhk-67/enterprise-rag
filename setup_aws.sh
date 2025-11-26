#!/bin/bash
# AWS Setup Helper Script

echo "🔧 AWS Setup Helper"
echo "=================="
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

echo "Please provide the following information:"
echo ""

read -p "AWS Access Key ID: " ACCESS_KEY
read -p "AWS Secret Access Key: " SECRET_KEY
read -p "S3 Bucket Name: " BUCKET_NAME
read -p "AWS Region (default: us-east-1): " REGION
REGION=${REGION:-us-east-1}

# Create .env file
cat > .env << EOF
# AWS Configuration
AWS_ACCESS_KEY_ID=$ACCESS_KEY
AWS_SECRET_ACCESS_KEY=$SECRET_KEY
AWS_DEFAULT_REGION=$REGION

# S3 Configuration
S3_BUCKET_NAME=$BUCKET_NAME
S3_RAW_DOCUMENTS_PREFIX=raw-documents
S3_PROCESSED_PREFIX=processed

# AWS Bedrock Configuration
BEDROCK_REGION=$REGION
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

# LLM Configuration
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ .env file created!"
echo ""
echo "Next steps:"
echo "1. Test connection: python scripts/test_aws_connection.py"
echo "2. Upload documents to S3: aws s3 cp document.pdf s3://$BUCKET_NAME/raw-documents/"
echo "3. Run the app: python app.py"


