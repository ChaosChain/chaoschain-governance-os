#!/bin/bash

echo "===== ChaosChain GitHub Cleanup Tool ====="
echo "This script helps prepare your repository for pushing to GitHub by cleaning up sensitive files."

# Make script executable
chmod +x cleanup_for_github.sh

# Check for changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Please commit or stash them before proceeding."
    git status
    exit 1
fi

echo "👍 No uncommitted changes detected."

# Check for sensitive files
echo "Checking for sensitive files..."

SENSITIVE_FILES=(
    "docker-compose.sepolia.yml"
    "docker-compose.staging.yml"
    "*private_key*"
    "*.key"
    "*.pem"
    "deployments/.env.sepolia"
    "deployments/.env.staging"
    "tx_hash.txt"
    "tmp_cmd.txt"
    "commit_fix_sepolia.sh"
    "commit-sepolia-anchoring.sh"
    "debug_jwt_issue.sh"
    "commit_changes.sh"
    "fix_jwt_auth.sh"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    files=$(find . -name "$pattern" 2>/dev/null | grep -v "node_modules" | grep -v ".git")
    if [ -n "$files" ]; then
        echo "⚠️  Found sensitive files matching pattern '$pattern':"
        echo "$files"
        echo ""
    fi
done

# Ensure docker-compose.example.yml exists
if [ ! -f "docker-compose.example.yml" ]; then
    echo "❌ docker-compose.example.yml is missing. This file should be included instead of the actual configuration."
    exit 1
else
    echo "✅ docker-compose.example.yml is present."
fi

# Ensure env.example exists
if [ ! -f "env.example" ]; then
    echo "❌ env.example is missing. This file should be included instead of actual .env files."
    exit 1
else
    echo "✅ env.example is present."
fi

# Check .gitignore to ensure it excludes sensitive files
for pattern in "${SENSITIVE_FILES[@]}"; do
    if ! grep -q "$pattern" .gitignore; then
        echo "⚠️  .gitignore doesn't contain pattern: $pattern"
    fi
done

echo ""
echo "===== Instructions for pushing to GitHub ====="
echo "1. Ensure you have committed all your code changes."
echo "2. Address any warnings above about sensitive files."
echo "3. Verify your .gitignore excludes all sensitive files."
echo "4. Run 'git add . && git commit -m \"Your commit message\"'"
echo "5. Run 'git push origin YOUR_BRANCH_NAME'"
echo ""
echo "Remember that even if files are in .gitignore, they may still be in the git history if they were committed previously."
echo "To remove sensitive files from git history, consider using tools like BFG Repo Cleaner."
echo "===== End of cleanup =====" 