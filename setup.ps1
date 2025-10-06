# BERT.CPP Docker Setup and Test Script for Windows PowerShell
# This script builds and runs the BERT.CPP Docker container

Write-Host "=== BERT.CPP Docker Setup ===" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "`nBuilding BERT.CPP Docker image..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting BERT.CPP container..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Container started successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start container!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Available Commands ===" -ForegroundColor Cyan
Write-Host "1. Enter interactive shell:" -ForegroundColor White
Write-Host "   docker exec -it bert-cpp-test /bin/bash" -ForegroundColor Gray

Write-Host "`n2. Run the test examples:" -ForegroundColor White
Write-Host "   docker exec -it bert-cpp-test /app/test.sh" -ForegroundColor Gray

Write-Host "`n3. Test dynamic library example:" -ForegroundColor White
Write-Host "   docker exec -it bert-cpp-test python3 examples/sample_dylib.py models/all-MiniLM-L6-v2/ggml-model-q4_0.bin" -ForegroundColor Gray

Write-Host "`n4. Start server (runs in background):" -ForegroundColor White
Write-Host "   docker exec -d bert-cpp-test ./build/bin/server -m models/all-MiniLM-L6-v2/ggml-model-q4_0.bin --port 8085" -ForegroundColor Gray

Write-Host "`n5. Test client (after server is running):" -ForegroundColor White
Write-Host "   docker exec -it bert-cpp-test python3 examples/sample_client.py 8085" -ForegroundColor Gray

Write-Host "`n6. Stop container:" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor Gray

Write-Host "`n=== Quick Test ===" -ForegroundColor Cyan
Write-Host "Running a quick test of the dynamic library..." -ForegroundColor Yellow

# Wait a moment for container to fully start
Start-Sleep -Seconds 3

# Run quick test
Write-Host "`nExecuting test..." -ForegroundColor Yellow
docker exec -it bert-cpp-test python3 examples/sample_dylib.py models/all-MiniLM-L6-v2/ggml-model-q4_0.bin

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "BERT.CPP is now running in Docker!" -ForegroundColor Green
Write-Host "Container name: bert-cpp-test" -ForegroundColor White
Write-Host "Port: 8085 (mapped to host)" -ForegroundColor White