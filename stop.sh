#!/bin/bash

# Flashcard App Cleanup Script

echo "🛑 Stopping Flashcard Learning App..."

# Kill any existing servers
echo "🧹 Cleaning up backend servers..."
pkill -f "uvicorn main:app"

echo "🧹 Cleaning up frontend servers..."
pkill -f "vite"

# Wait a moment for processes to terminate
sleep 2

# Check if any processes are still running
BACKEND_RUNNING=$(pgrep -f "uvicorn main:app" | wc -l)
FRONTEND_RUNNING=$(pgrep -f "vite" | wc -l)

if [ $BACKEND_RUNNING -eq 0 ] && [ $FRONTEND_RUNNING -eq 0 ]; then
    echo "✅ All servers stopped successfully!"
    echo "🔌 Port 8001 (backend) is now free"
    echo "🔌 Port 5173 (frontend) is now free"
else
    echo "⚠️  Some processes may still be running. Try again or restart your terminal."
fi

echo "🎯 You can now restart the app with ./start.sh"
