#!/bin/bash

# Script to push ClickUp Task Numbering to GitHub
# Run this script from the directory containing your project files

echo "Setting up git repository..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    git branch -m main
fi

# Configure git
git config user.name "soothill"
git config user.email "soothill@users.noreply.github.com"

# Add all files
echo "Adding files..."
git add clickup_numbering.py requirements.txt README.md .gitignore

# Commit
echo "Creating commit..."
git commit -m "Initial commit: ClickUp epic and task numbering script" 2>/dev/null || echo "Files already committed"

# Add remote
echo "Adding GitHub remote..."
git remote remove origin 2>/dev/null
git remote add origin https://github.com/soothill/clickup-task-numbering.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✓ Successfully pushed to https://github.com/soothill/clickup-task-numbering"
