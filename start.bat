@echo off
REM SMC Trading Bot - Startup Script
REM Date: 4 Nov 2025

echo ========================================
echo SMC Trading Bot - HIGH VOLUME MARKETS
echo ========================================
echo.

echo [1/3] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Checking dependencies...
python -c "import fastapi, uvicorn, requests, dotenv" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Dependencies missing. Installing...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo.
echo [3/3] Starting FastAPI server...
echo.
echo Bot is running on: http://localhost:8000
echo Health check: http://localhost:8000/health
echo Webhook endpoint: http://localhost:8000/tv
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
