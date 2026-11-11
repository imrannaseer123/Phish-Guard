@echo off
title PhishGuard Web Application
chcp 65001 >nul

echo ======================================================================
echo   🛡️  PhishGuard — Starting Application
echo ======================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%SCRIPT_DIR%.venv\Scripts\python.exe"
    echo [INFO] Using virtual environment Python: .venv
) else (
    set "PYTHON_CMD=python"
    echo [INFO] Using system Python
)

echo [INFO] Starting web server on http://127.0.0.1:5000 ...
"%PYTHON_CMD%" run.py %*

pause

