Write-Host "===================================================" -ForegroundColor Green
Write-Host "Launching Smart Canteen Full-Stack System" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

$RootPath = $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\backend'; python -m pip install -r requirements.txt; python -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\frontend'; npm install; npm run dev"

Write-Host "`nBoth servers are launching:" -ForegroundColor Cyan
Write-Host "- Frontend Portal: http://localhost:3000" -ForegroundColor Yellow
Write-Host "- Backend API & Swagger: http://localhost:8000/docs" -ForegroundColor Yellow
