@echo off
echo === BERT.CPP Docker Setup ===

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo Docker is running...

echo.
echo Building BERT.CPP Docker image...
docker-compose build

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Starting BERT.CPP container...
docker-compose up -d

if errorlevel 1 (
    echo Failed to start container!
    pause
    exit /b 1
)

echo.
echo === Setup Complete ===
echo BERT.CPP is now running in Docker!
echo.
echo Available commands:
echo 1. Enter interactive shell: docker exec -it bert-cpp-test /bin/bash
echo 2. Run test examples: docker exec -it bert-cpp-test /app/test.sh
echo 3. Stop container: docker-compose down
echo.

REM Wait a moment then run quick test
echo Running quick test in 3 seconds...
timeout /t 3 /nobreak >nul

echo Testing dynamic library example...
docker exec -it bert-cpp-test python3 examples/sample_dylib.py models/all-MiniLM-L6-v2/ggml-model-q4_0.bin

pause