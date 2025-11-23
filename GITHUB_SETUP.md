# GitHub Repository Setup Guide

## 🎯 Quick Answer: **Use Terminal** (Recommended)

Terminal is faster, more consistent, and gives you better control. Here's how to do it:

---

## ✅ **Method 1: Terminal (Recommended)**

### Step 1: Navigate to Project Directory
```bash
cd /Users/avdhootkulkarni/Desktop/RAG
```

### Step 2: Initialize Git (if not already done)
```bash
# Check if git is already initialized
git status

# If not initialized, run:
git init
```

### Step 3: Add All Files (except .env)
```bash
# Add all files
git add .

# Verify what's being added (make sure .env is NOT included)
git status
```

### Step 4: Create Initial Commit
```bash
git commit -m "Initial commit: Enterprise Document QA and Search Assistant"
```

### Step 5: Create Repository on GitHub

**Option A: Using GitHub CLI (if installed)**
```bash
# Install GitHub CLI if needed: brew install gh
gh auth login
gh repo create enterprise-rag --public --source=. --remote=origin --push
```

**Option B: Manual GitHub Creation + Push**
```bash
# 1. Go to github.com and create a new repository (don't initialize with README)
# 2. Copy the repository URL (e.g., https://github.com/yourusername/enterprise-rag.git)
# 3. Add remote and push:

git remote add origin https://github.com/yourusername/enterprise-rag.git
git branch -M main
git push -u origin main
```

---

## 📋 **Method 2: Manual (GitHub Website)**

### Steps:
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name: `enterprise-rag` (or your preferred name)
4. Description: "Enterprise Document QA and Search Assistant with AWS, RAG, and Generative AI"
5. Choose: Public or Private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"
8. Follow the "push an existing repository" instructions shown on GitHub

---

## 🔒 **IMPORTANT: Before Pushing - Security Checklist**

### ✅ Check These Before Committing:

1. **Verify .env is NOT tracked:**
```bash
# Check if .env is in git
git ls-files | grep .env

# If it shows .env, remove it:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

2. **Verify .gitignore includes:**
```bash
# Check .gitignore content
cat .gitignore

# Should include:
# - .env
# - .env.local
# - data/
# - *.faiss
# - *.index
```

3. **Check for any AWS credentials in files:**
```bash
# Search for potential secrets
grep -r "AWS_ACCESS_KEY" . --exclude-dir=.git
grep -r "AWS_SECRET" . --exclude-dir=.git
```

---

## 📝 **Recommended Repository Settings**

### Repository Name:
```
enterprise-rag
```
or
```
enterprise-document-qa
```

### Description:
```
Enterprise Document QA and Search Assistant - Production-ready RAG system with AWS, Generative AI, and advanced retrieval techniques
```

### Topics/Tags (add these on GitHub):
- `rag`
- `retrieval-augmented-generation`
- `aws`
- `bedrock`
- `langchain`
- `fastapi`
- `vector-search`
- `document-qa`
- `claude`
- `python`

### Visibility:
- **Public**: Good for portfolio, learning, open source
- **Private**: If contains sensitive business logic

---

## 📄 **Files to Include/Exclude**

### ✅ **Include:**
- All source code (`src/`)
- Configuration files (`config/`)
- Documentation (`*.md` files)
- `requirements.txt`
- `app.py`
- `scripts/`
- `examples/`
- `.gitignore`
- `README.md`

### ❌ **Exclude (via .gitignore):**
- `.env` (contains AWS credentials)
- `.env.local`
- `data/` (FAISS indexes, local data)
- `*.faiss` (vector index files)
- `*.index`
- `*.metadata.json`
- `__pycache__/`
- `*.pyc`
- `.venv/` or `venv/`
- `logs/`

---

## 🚀 **Complete Terminal Workflow**

```bash
# 1. Navigate to project
cd /Users/avdhootkulkarni/Desktop/RAG

# 2. Initialize git (if needed)
git init

# 3. Check .gitignore is working
git status

# 4. Add all files
git add .

# 5. Verify .env is NOT included
git status | grep .env
# Should return nothing

# 6. Create initial commit
git commit -m "Initial commit: Enterprise Document QA and Search Assistant

- Complete RAG pipeline with AWS integration
- S3 document ingestion
- Bedrock embeddings and LLM generation
- Vector search with FAISS/OpenSearch
- FastAPI REST API
- Quality validation system
- Comprehensive documentation"

# 7. Create repo on GitHub (using GitHub CLI)
gh repo create enterprise-rag --public --source=. --remote=origin --push

# OR manually:
# 7a. Create repo on github.com
# 7b. Then run:
git remote add origin https://github.com/YOUR_USERNAME/enterprise-rag.git
git branch -M main
git push -u origin main
```

---

## 📋 **Post-Setup Checklist**

After creating the repo:

- [ ] Verify `.env` is NOT in repository
- [ ] Add repository description on GitHub
- [ ] Add topics/tags
- [ ] Update README.md if needed
- [ ] Consider adding LICENSE file
- [ ] Add `.env.example` file (template without real credentials)
- [ ] Verify all documentation files are included

---

## 🔧 **Adding .env.example Template**

Create a template file for others:

```bash
# Create .env.example from template
cp .env.example .env.example.template 2>/dev/null || echo "Creating .env.example"

# Or create it manually with placeholder values
cat > .env.example << 'EOF'
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-company-documents-rag

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# Vector Database
VECTOR_DB_TYPE=faiss
FAISS_INDEX_PATH=./data/faiss_index
EOF

git add .env.example
git commit -m "Add .env.example template"
git push
```

---

## 🎯 **Quick Commands Reference**

```bash
# Check what will be committed
git status

# See what's in .gitignore
cat .gitignore

# Verify .env is ignored
git check-ignore .env
# Should output: .env

# View commit history
git log --oneline

# Push changes
git push

# Pull changes (if working from multiple machines)
git pull
```

---

## ⚠️ **Common Mistakes to Avoid**

1. **Don't commit .env file** - Contains sensitive credentials
2. **Don't commit data/ directory** - Contains large index files
3. **Don't commit virtual environment** - venv/ or .venv/
4. **Don't initialize with README on GitHub** - We already have one
5. **Do verify .gitignore is working** before first commit

---

## 🆘 **If You Already Pushed .env by Mistake**

```bash
# Remove from git (but keep local file)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from repository"

# Push the fix
git push

# IMPORTANT: Rotate your AWS credentials immediately!
# The old credentials are now in git history
```

---

## 📚 **Recommended Repository Structure (Final)**

```
enterprise-rag/
├── .git/                    # Git metadata
├── .gitignore               # ✅ Included
├── .env.example             # ✅ Included (template)
├── .env                     # ❌ NOT included (local only)
├── src/                     # ✅ Included
├── config/                  # ✅ Included
├── scripts/                 # ✅ Included
├── examples/                # ✅ Included
├── data/                    # ❌ NOT included (local only)
├── app.py                   # ✅ Included
├── requirements.txt         # ✅ Included
├── README.md               # ✅ Included
├── AWS_SETUP.md            # ✅ Included
├── PROJECT_OVERVIEW.md     # ✅ Included
└── ... (other docs)        # ✅ Included
```

---

## ✅ **Final Recommendation**

**Use Terminal Method** because:
- ✅ Faster and more efficient
- ✅ Better for version control workflow
- ✅ Easier to automate
- ✅ More professional
- ✅ Better for future updates

**Steps:**
1. Verify `.gitignore` is correct
2. Initialize git (if needed)
3. Add and commit files
4. Create repo on GitHub (CLI or manual)
5. Push to GitHub

**Time:** ~5 minutes

---

Ready to create your repo? Follow the "Complete Terminal Workflow" section above! 🚀

