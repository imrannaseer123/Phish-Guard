# PhishGuard PowerShell Runner
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[INFO] Using virtual environment Python (.venv)" -ForegroundColor Green
    $pythonCmd = $venvPython
} else {
    Write-Host "[INFO] Using system Python" -ForegroundColor Yellow
    $pythonCmd = "python"
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  🛡️  PhishGuard — Launching Application" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Open your browser at: http://127.0.0.1:5000" -ForegroundColor White

& $pythonCmd run.py @args

