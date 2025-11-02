#!/bin/bash

# Infosphere Development Startup Script

echo "🌐 Starting Infosphere Development Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment (Windows)
echo "📦 Activating Python virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Start backend
echo "🚀 Starting FastAPI backend..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "⚡ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Infosphere is starting up!"
echo "📊 Backend API: http://localhost:8000"
echo "🎨 Frontend App: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo '🔄 Shutting down services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait