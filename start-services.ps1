Write-Host "Starting SimilarWeb Simulator..." -ForegroundColor Green
Write-Host ""

Write-Host "Starting FastAPI Backend..." -ForegroundColor Yellow
Start-Process -WindowStyle Normal -FilePath "cmd" -ArgumentList "/k", "cd /d backend && python main.py"

Write-Host "Waiting for backend to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host "Starting Next.js Frontend..." -ForegroundColor Yellow
Start-Process -WindowStyle Normal -FilePath "cmd" -ArgumentList "/k", "pnpm dev"

Write-Host ""
Write-Host "Both services are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
