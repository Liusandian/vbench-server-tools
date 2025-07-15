@echo off
echo Starting Camera Motion Evaluation Server...
echo =========================================

cd /d "%~dp0"

REM 检查Python是否存在
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python first.
    pause
    exit /b 1
)

REM 检查requirements.txt是否存在
if not exist requirements.txt (
    echo Error: requirements.txt not found.
    pause
    exit /b 1
)

REM 安装依赖（如果需要）
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting server at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python server.py

echo.
echo Server stopped.
pause 