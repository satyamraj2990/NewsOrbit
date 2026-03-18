# GDELT PyR Web Dashboard Launcher
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   🌍 GDELT PyR Web Dashboard" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📡 Server URL: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:5000"
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Red
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

python app.py
