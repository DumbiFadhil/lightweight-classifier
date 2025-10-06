# Lightweight Indonesian Query Classifier Setup Script
# This script builds and runs the lightweight DistilBERT Docker container

Write-Host "=== Lightweight Indonesian Query Classifier Setup ===" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "`nBuilding lightweight Indonesian classifier image..." -ForegroundColor Yellow
docker-compose -f docker-compose.light.yml build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting Indonesian classifier container..." -ForegroundColor Yellow
docker-compose -f docker-compose.light.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Container started successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Available Commands ===" -ForegroundColor Cyan

Write-Host "1. Test the classifier:" -ForegroundColor White
Write-Host "   docker exec -it indonesian-classifier python src/test.py" -ForegroundColor Gray

Write-Host "`n2. Start API server:" -ForegroundColor White
Write-Host "   docker exec -d indonesian-classifier python src/main.py" -ForegroundColor Gray

Write-Host "`n3. Test API endpoints:" -ForegroundColor White
Write-Host "   curl http://localhost:8080/health" -ForegroundColor Gray
Write-Host "   curl http://localhost:8080/operations" -ForegroundColor Gray
Write-Host "   curl http://localhost:8080/examples" -ForegroundColor Gray

Write-Host "`n4. Interactive shell:" -ForegroundColor White
Write-Host "   docker exec -it indonesian-classifier /bin/bash" -ForegroundColor Gray

Write-Host "`n5. View API documentation:" -ForegroundColor White
Write-Host "   Open browser: http://localhost:8080/docs" -ForegroundColor Gray

Write-Host "`n6. Stop container:" -ForegroundColor White
Write-Host "   docker-compose -f docker-compose.light.yml down" -ForegroundColor Gray

Write-Host "`n=== Quick Test ===" -ForegroundColor Cyan
Write-Host "Running classifier test..." -ForegroundColor Yellow

# Wait for container to start
Start-Sleep -Seconds 5

# Run quick test
Write-Host "`nTesting Indonesian query classification..." -ForegroundColor Yellow
docker exec -it indonesian-classifier python src/test.py

Write-Host "`n=== Lightweight Setup Complete ===" -ForegroundColor Green
Write-Host "Indonesian Query Classifier is now running!" -ForegroundColor Green
Write-Host "Container: indonesian-classifier" -ForegroundColor White
Write-Host "API Port: 8080" -ForegroundColor White
Write-Host "Memory Usage: ~300-500MB (much lighter than full bert.cpp!)" -ForegroundColor White