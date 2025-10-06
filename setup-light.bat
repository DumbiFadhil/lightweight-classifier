@echo off
echo === Lightweight Indonesian Query Classifier Setup ===

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo Docker is running...

echo.
echo Building lightweight Indonesian classifier image...
docker-compose -f docker-compose.light.yml build

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Starting Indonesian classifier container...
docker-compose -f docker-compose.light.yml up -d

if errorlevel 1 (
    echo Failed to start container!
    pause
    exit /b 1
)

echo.
echo === Setup Complete ===
echo Indonesian Query Classifier is now running!
echo.
echo Available commands:
echo 1. Test classifier: docker exec -it indonesian-classifier python src/test.py
echo 2. Start API server: docker exec -d indonesian-classifier python src/main.py  
echo 3. API docs: http://localhost:8080/docs
echo 4. Stop container: docker-compose -f docker-compose.light.yml down
echo.

REM Wait a moment then run quick test
echo Running classifier test in 5 seconds...
timeout /t 5 /nobreak >nul

echo Testing Indonesian query classification...
docker exec -it indonesian-classifier python src/test.py

echo.
echo === Lightweight classifier is ready! ===
echo Memory usage: ~300-500MB (much lighter than full BERT!)
echo API available at: http://localhost:8080
pause