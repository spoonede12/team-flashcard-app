#!/bin/bash

# Flashcard App Startup Script

echo "🚀 Starting Flashcard Learning App..."

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Kill any existing servers
echo "🧹 Cleaning up existing servers..."
pkill -f "uvicorn main:app"
pkill -f "vite"

# Start backend server
echo "🔧 Starting Python backend server..."
cd backend
source "../.venv/bin/activate"
python -m uvicorn main:app --reload --port 8001 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend server
echo "⚛️  Starting React frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Application started successfully!"
echo "📱 Frontend: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop
trap 'echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

wait
