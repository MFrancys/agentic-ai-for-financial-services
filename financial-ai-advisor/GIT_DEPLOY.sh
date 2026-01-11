#!/bin/bash
# Git Deployment Script for Financial AI Advisor

echo "🚀 Deploying Financial AI Advisor to GitHub..."

# Navigate to project directory
cd /Users/mfrancys/Documents/2026/financial-ai-advisor

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Check if .env file exists and warn user
if [ -f ".env" ]; then
    echo "⚠️  WARNING: .env file exists - make sure it's in .gitignore!"
    echo "   Checking .gitignore..."
    if grep -q "^.env$" .gitignore; then
        echo "   ✅ .env is in .gitignore - safe to proceed"
    else
        echo "   ❌ ERROR: .env NOT in .gitignore! Aborting."
        exit 1
    fi
fi

# Stage all files
echo "📝 Staging files..."
git add .

# Show status
echo ""
echo "📋 Git Status:"
git status

# Commit
echo ""
read -p "💬 Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Initial commit - Financial AI Advisor production app"
fi

git commit -m "$commit_msg"

# Add remote (if not already added)
echo ""
echo "🔗 Setting up remote repository..."
git remote remove origin 2>/dev/null  # Remove if exists
git remote add origin https://github.com/MFrancys/financial-ai-advisor.git

# Rename branch to main
git branch -M main

# Push to GitHub
echo ""
echo "⬆️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎉 Your project is now on GitHub:"
echo "   https://github.com/MFrancys/financial-ai-advisor"
echo ""
echo "📝 Next Steps:"
echo "   1. Add screenshots to README"
echo "   2. Deploy to Streamlit Cloud (streamlit.io/cloud)"
echo "   3. Update README with live demo URL"
echo ""

