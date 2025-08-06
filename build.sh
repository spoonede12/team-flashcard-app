#!/bin/bash

# Build script for deployment
echo "Starting build process..."

# Install Python dependencies
pip install --no-cache-dir -r requirements.txt

# Change to backend directory and start server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
