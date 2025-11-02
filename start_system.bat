@echo off
echo Starting Infosphere System...

echo Starting Backend Server...
start "Backend" cmd /c "cd /d C:\project\infosphere && C:\project\infosphere\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8001"

timeout /t 3

echo Starting Frontend Server...
start "Frontend" cmd /c "cd /d C:\project\infosphere\frontend && npm start"

echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo News Page: http://localhost:3000/news

pause