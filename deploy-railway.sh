#!/bin/bash

# Quick Deploy to Railway Script

echo "🚄 Deploying to Railway..."

# Build production version
echo "🏗️  Building for production..."
./build-production.sh

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

echo "🚀 Deploying to Railway..."
echo "Visit https://railway.app to:"
echo "1. Connect your GitHub repository"
echo "2. Deploy automatically"
echo ""
echo "Or use Railway CLI:"
echo "npm install -g @railway/cli"
echo "railway login"
echo "railway deploy"
