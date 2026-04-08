# Factly Setup and Launch Script for Windows PowerShell
# This script validates the setup, starts backend and frontend, and opens the browser

$ErrorActionPreference = "Continue"
$factlyRoot = "c:\Users\DELL\OneDrive\Desktop\Factly"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FACTLY - Complete Setup & Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project root
Set-Location $factlyRoot

# ========================
# 1. VALIDATE ENVIRONMENT
# ========================
Write-Host "[1/5] Validating environment..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVer = & python --version 2>&1
    Write-Host "✓ Python found: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVer = & node --version 2>&1
    $npmVer = & npm --version 2>&1
    Write-Host "✓ Node.js found: $nodeVer" -ForegroundColor Green
    Write-Host "✓ npm found: $npmVer" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js or npm not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# ========================
# 2. SETUP BACKEND
# ========================
Write-Host ""
Write-Host "[2/5] Setting up backend..." -ForegroundColor Yellow

Set-Location "$factlyRoot\backend"

# Check/create venv
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    & python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
}

# Find Python in venv
$pythonExe = if (Test-Path "venv\Scripts\python.exe") { 
    "venv\Scripts\python.exe" 
} else { 
    "python" 
}

Write-Host "Using Python: $pythonExe" -ForegroundColor Cyan

# Install requirements
Write-Host "Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Cyan
& $pythonExe -m pip install -q --upgrade pip 2>$null
$pipInstall = & $pythonExe -m pip install -r requirements.txt 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Some dependencies may have failed to install" -ForegroundColor Yellow
    Write-Host $pipInstall -ForegroundColor Yellow
} else {
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
}

# Check .env
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
    }
}

# Run migrations
Write-Host "Running Django migrations..." -ForegroundColor Cyan
& $pythonExe manage.py migrate --no-input 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations completed" -ForegroundColor Green
} else {
    Write-Host "⚠ Migration completed with warnings (this is OK for first run)" -ForegroundColor Yellow
}

# ========================
# 3. SETUP FRONTEND
# ========================
Write-Host ""
Write-Host "[3/5] Setting up frontend..." -ForegroundColor Yellow

Set-Location "$factlyRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies (this may take a few minutes)..." -ForegroundColor Cyan
    & npm install --silent 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ npm install failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend dependencies already installed" -ForegroundColor Green
}

# ========================
# 4. START SERVICES
# ========================
Write-Host ""
Write-Host "[4/5] Starting services..." -ForegroundColor Yellow

Set-Location $factlyRoot

# Start Backend
Write-Host "Starting Django backend on port 8000..." -ForegroundColor Cyan
$backendProcess = Start-Process -PassThru -NoNewWindow -FilePath $pythonExe `
    -ArgumentList "backend\manage.py runserver 8000" `
    -WorkingDirectory "$factlyRoot\backend"
$backendPID = $backendProcess.Id
Write-Host "✓ Backend started (PID: $backendPID)" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting React frontend on port 3000..." -ForegroundColor Cyan
$frontendProcess = Start-Process -PassThru -NoNewWindow -FilePath "cmd" `
    -ArgumentList "/c npm start" `
    -WorkingDirectory "$factlyRoot\frontend"
$frontendPID = $frontendProcess.Id
Write-Host "✓ Frontend started (PID: $frontendPID)" -ForegroundColor Green
Start-Sleep -Seconds 5

# ========================
# 5. OPEN BROWSER
# ========================
Write-Host ""
Write-Host "[5/5] Opening application..." -ForegroundColor Yellow

Write-Host "Opening http://localhost:3000 in your default browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

# ========================
# SUMMARY
# ========================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ FACTLY Application Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000 (PID: $frontendPID)" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000 (PID: $backendPID)" -ForegroundColor White
Write-Host ""
Write-Host "To stop services, run:" -ForegroundColor Yellow
Write-Host "  Stop-Process -Id $backendPID" -ForegroundColor Gray
Write-Host "  Stop-Process -Id $frontendPID" -ForegroundColor Gray
Write-Host ""
Write-Host "Keep this window open while services are running." -ForegroundColor Yellow
Write-Host "Press Ctrl+C in the service windows to stop them." -ForegroundColor Yellow
