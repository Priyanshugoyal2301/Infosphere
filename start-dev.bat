@echo off
REM Infosphere Development Startup Script for Windows

echo 🌐 Starting Infosphere Development Environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup first.
    exit /b 1
)

REM Activate virtual environment
echo 📦 Activating Python virtual environment...
call venv\Scripts\activate.bat

REM Start backend
echo 🚀 Starting FastAPI backend...
cd backend
start "Infosphere Backend" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM Wait a moment for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend
echo ⚡ Starting React frontend...
cd frontend
start "Infosphere Frontend" cmd /k "npm start"
cd ..

echo ✅ Infosphere is starting up!
echo 📊 Backend API: http://localhost:8000
echo 🎨 Frontend App: http://localhost:3000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause > nul