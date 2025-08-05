#!/bin/bash

# Production Build Script for Flashcard App

echo "🏗️  Building Flashcard App for Production..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf backend/static
rm -rf frontend/dist

# Build frontend
echo "⚛️  Building React frontend..."
cd frontend
npm run build

# Copy built frontend to backend static directory
echo "📁 Copying frontend build to backend..."
cd ..
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "✅ Production build complete!"
echo "📦 Files ready for deployment in backend/ directory"
echo ""
echo "🚀 Deploy options:"
echo "1. Docker: docker build -t flashcard-app ."
echo "2. Upload backend/ folder to your hosting service"
echo "3. Run: python -m uvicorn main:app --host 0.0.0.0 --port 8000"
