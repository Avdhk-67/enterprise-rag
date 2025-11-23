# Setup Checklist - Can You Run the Code Now?

## ❌ **NO - You need to complete these steps first:**

### ✅ Step 1: Install Python Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```
**Status**: Can do this now - no AWS needed yet

### ✅ Step 2: Create .env File (1 minute)
Create a file named `.env` in the project root with this content:

```bash
# AWS Configuration (you'll fill these in Step 4)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-company-documents-rag

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Vector Database (use FAISS for local testing - no AWS setup needed)
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index
```

**Status**: Can create this now, but will need to update with real values

### ⚠️ Step 3: Run Setup Script (1 minute)
```bash
python scripts/setup.py
```
This creates necessary directories.

**Status**: Can do this now

### ❌ Step 4: AWS Setup (15-30 minutes) - **REQUIRED**

You **MUST** complete AWS setup before the code will work:

#### 4a. Create S3 Bucket (5 min)
```bash
aws s3 mb s3://your-company-documents-rag --region us-east-1
```
Update `.env` with your bucket name.

#### 4b. Request Bedrock Access (10 min)
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" → "Edit"
3. Request access to:
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Amazon Titan Embeddings
4. Wait for approval (Titan is usually instant, Claude may take time)

#### 4c. Create IAM User & Get Credentials (5 min)
```bash
# Create user
aws iam create-user --user-name rag-application-user

# Create access key (SAVE THE OUTPUT!)
aws iam create-access-key --user-name rag-application-user

# Attach S3 policy
aws iam attach-user-policy \
  --user-name rag-application-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

Then create a Bedrock policy (see `AWS_SETUP.md` for full policy).

**Update `.env` with your access keys.**

### ✅ Step 5: Test Connections (1 minute)
```bash
python scripts/test_aws_connection.py
```

**Status**: Can only do this AFTER Step 4 is complete

---

## 🎯 **What You Can Do RIGHT NOW (Without AWS):**

### Option 1: Test Code Structure (No AWS Needed)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file (use placeholder values)
# 3. Run setup
python scripts/setup.py

# 4. Try importing (will fail on AWS connection, but tests code structure)
python -c "from src.rag_pipeline import RAGPipeline; print('Import successful!')"
```

### Option 2: Review and Understand Code
- Read through `README.md`
- Check `AWS_SETUP.md` for detailed instructions
- Review `PROJECT_SUMMARY.md` for architecture

---

## 🚦 **Current Status:**

| Component | Status | Can Run? |
|-----------|--------|----------|
| Code Structure | ✅ Complete | Yes (imports work) |
| Dependencies | ⏳ Need to install | Run `pip install -r requirements.txt` |
| .env File | ⏳ Need to create | Create manually |
| AWS S3 | ❌ Not set up | **Required** |
| AWS Bedrock | ❌ Not set up | **Required** |
| IAM Credentials | ❌ Not set up | **Required** |
| Vector DB | ⏳ Can use FAISS | Works locally |

---

## ✅ **Minimum to Run (Local Testing with FAISS):**

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create `.env` file with FAISS config (no AWS needed for FAISS)
3. ✅ Run setup: `python scripts/setup.py`
4. ❌ **Still need AWS for:**
   - Document ingestion from S3
   - Bedrock LLM for generation
   - Bedrock embeddings

**Even with FAISS, you still need AWS Bedrock for the LLM and embeddings!**

---

## 🎯 **Recommended Path:**

1. **Now**: Install dependencies and create `.env` file
2. **Now**: Review AWS setup documentation
3. **Next**: Complete AWS setup (S3, Bedrock, IAM)
4. **Then**: Test connections
5. **Finally**: Run the application

---

## ⚡ **Quick Test (After AWS Setup):**

```bash
# 1. Test connections
python scripts/test_aws_connection.py

# 2. If all pass, try running the app
python app.py

# 3. In another terminal, test the API
curl http://localhost:8000/health
```

---

## 🆘 **If You Get Errors:**

### "ModuleNotFoundError"
→ Run: `pip install -r requirements.txt`

### "AWS credentials not found"
→ Create `.env` file and add AWS credentials

### "Access Denied" to Bedrock
→ Request model access in Bedrock console

### "Bucket not found"
→ Create S3 bucket and update `.env`

### "No module named 'faiss'"
→ Install: `pip install faiss-cpu`

---

## 📝 **Summary:**

**Can you run it now?** ❌ **Not fully** - you need AWS setup first.

**What works now?**
- ✅ Code structure is complete
- ✅ You can install dependencies
- ✅ You can review the code

**What's needed?**
- ❌ AWS S3 bucket
- ❌ AWS Bedrock access
- ❌ IAM credentials
- ⏳ `.env` file configuration

**Estimated time to get running:** 20-30 minutes (mostly AWS setup)

---

**Next Step**: Follow `AWS_QUICK_START.md` for fastest setup path!

