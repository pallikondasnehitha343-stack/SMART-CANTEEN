@echo off
title Smart Canteen System Launcher
echo ===================================================
echo Launching Smart Canteen Full-Stack System
echo ===================================================

echo Starting Backend in a new window...
start "Smart Canteen Backend (Port 8000)" "%~dp0start_backend.bat"

echo Starting Frontend in a new window...
start "Smart Canteen Frontend (Port 3000)" "%~dp0start_frontend.bat"

echo.
echo ===================================================
echo Both servers are launching:
echo - Frontend: http://localhost:3000
echo - Backend API & Docs: http://localhost:8000/docs
echo ===================================================
timeout /t 5
