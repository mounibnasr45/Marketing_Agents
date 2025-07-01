@echo off
echo Starting SimilarWeb Simulator...
echo.

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d backend && python main.py"

echo Waiting for backend to start...
ping 127.0.0.1 -n 4 > nul

echo Starting Next.js Frontend...
start "Next.js Frontend" cmd /k "pnpm dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul
