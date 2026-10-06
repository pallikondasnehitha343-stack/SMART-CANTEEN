@echo off
title Smart Canteen Automated Verification
echo ===================================================
echo Running Smart Canteen Automated Test Suite & Matrix
echo ===================================================
cd /d "%~dp0\backend"

python test_runner.py

pause
