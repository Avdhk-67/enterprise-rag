#!/bin/bash
# Quick GitHub Repository Setup Script
# Run this from the project root directory

echo "🚀 Setting up GitHub repository..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this from the project root directory."
    exit 1
fi

# Step 1: Initialize Git
echo "📦 Step 1: Initializing Git repository..."
git init

# Step 2: Verify .env is in .gitignore
echo ""
echo "🔒 Step 2: Verifying .env is ignored..."
if git check-ignore .env > /dev/null 2>&1; then
    echo "✅ .env is properly ignored"
else
    echo "⚠️  Warning: .env might not be ignored. Check .gitignore file."
fi

# Step 3: Add all files
echo ""
echo "📝 Step 3: Adding files to Git..."
git add .

# Step 4: Show what will be committed (verify .env is NOT included)
echo ""
echo "📋 Step 4: Files to be committed:"
git status --short | head -20
echo "..."

# Check if .env is accidentally included
if git ls-files | grep -q "^\.env$"; then
    echo ""
    echo "❌ ERROR: .env file is being tracked! Removing it..."
    git rm --cached .env
    echo "✅ Removed .env from tracking"
fi

# Step 5: Create initial commit
echo ""
echo "💾 Step 5: Creating initial commit..."
git commit -m "Initial commit: Enterprise Document QA and Search Assistant

- Complete RAG pipeline with AWS integration
- S3 document ingestion
- Bedrock embeddings and LLM generation
- Vector search with FAISS/OpenSearch
- FastAPI REST API
- Quality validation system
- Comprehensive documentation"

echo ""
echo "✅ Git repository initialized and committed!"
echo ""
echo "📤 Next steps:"
echo ""
echo "Option 1: Using GitHub CLI (recommended)"
echo "  1. Install GitHub CLI: brew install gh"
echo "  2. Authenticate: gh auth login"
echo "  3. Create repo: gh repo create enterprise-rag --public --source=. --remote=origin --push"
echo ""
echo "Option 2: Manual GitHub setup"
echo "  1. Go to https://github.com/new"
echo "  2. Create a new repository (don't initialize with README)"
echo "  3. Copy the repository URL"
echo "  4. Run these commands:"
echo "     git remote add origin https://github.com/YOUR_USERNAME/enterprise-rag.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "🔒 Security reminder: Make sure .env file is NOT in the repository!"

