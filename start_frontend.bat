@echo off
title Smart Canteen Next.js Frontend
echo ===================================================
echo Starting Smart Canteen Next.js Frontend
echo ===================================================
cd /d "%~dp0\frontend"

echo Checking and installing npm packages...
call npm install

echo Launching Next.js development server on http://localhost:3000 ...
call npm run dev

pause
