@echo off
title Smart Canteen Backend Server
echo ===================================================
echo Starting Smart Canteen Python FastAPI Backend Server
echo ===================================================
cd /d "%~dp0\backend"

echo Checking Python dependencies...
python -m pip install -r requirements.txt

echo Starting Uvicorn server on http://localhost:8000 ...
python -m uvicorn app.main:app --reload --port 8000

pause
