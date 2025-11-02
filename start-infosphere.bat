@echo off
echo 🌟 Starting Infosphere Platform...
echo ================================

REM Kill any existing processes on ports 3000 and 8000
echo 🔄 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

echo 🚀 Starting Backend Service...
cd backend
start "Infosphere Backend" cmd /k "..\venv\Scripts\python.exe main.py"
timeout /t 10 >nul

echo 🎨 Starting Frontend Service...
cd ..\frontend
start "Infosphere Frontend" cmd /k "npm start"
timeout /t 5 >nul

echo ✅ Services starting...
echo 🌐 Frontend will be available at: http://localhost:3000
echo 📡 Backend API will be available at: http://localhost:8000/docs
echo.
echo 💡 Wait for both services to fully load, then test the application!
echo 📝 Check the terminal windows for startup progress.
pause