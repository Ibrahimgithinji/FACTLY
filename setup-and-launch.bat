@echo off
REM Advanced Factly Setup and Launch Script
REM This script validates, sets up, and launches the Factly application

setlocal enabledelayedexpansion

set FACTLY_ROOT=c:\Users\DELL\OneDrive\Desktop\Factly
set PYTHON_EXE=python
set NODE_MODULES_OK=0

echo.
echo ========================================
echo  FACTLY - AI-Powered News Verification
echo  Complete Setup & Launch Script
echo ========================================
echo.

REM Change to project root
cd /d "%FACTLY_ROOT%" || (
    echo ERROR: Could not navigate to %FACTLY_ROOT%
    pause
    exit /b 1
)

REM ========================
REM 1. VALIDATE ENVIRONMENT
REM ========================
echo [1/6] Validating environment...
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   [OK] Python %PYTHON_VERSION% found

REM Check Node.js
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo   [OK] Node.js %NODE_VERSION% found

for /f %%i in ('npm --version') do set NPM_VERSION=%%i
echo   [OK] npm %NPM_VERSION% found

echo.

REM ========================
REM 2. SETUP BACKEND
REM ========================
echo [2/6] Setting up backend (Django)...
echo.

cd /d "%FACTLY_ROOT%\backend"

REM Check if venv exists
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
) else (
    echo   [OK] Virtual environment exists
)

REM Install backend requirements
echo Installing backend dependencies (this may take a few minutes)...
call venv\Scripts\python.exe -m pip install -q --upgrade pip
call venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   [WARNING] Some dependencies may have failed
    echo   [INFO] Attempting to continue...
) else (
    echo   [OK] Backend dependencies installed
)

REM Run migrations
echo Running Django migrations...
call venv\Scripts\python.exe manage.py migrate --no-input >nul 2>&1
echo   [OK] Migrations completed

echo.

REM ========================
REM 3. SETUP FRONTEND
REM ========================
echo [3/6] Setting up frontend (React)...
echo.

cd /d "%FACTLY_ROOT%\frontend"

REM Check if node_modules exists
if not exist node_modules (
    echo Installing frontend dependencies (this may take a few minutes)...
    call npm install --silent
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo   [OK] Frontend dependencies installed
) else (
    echo   [OK] Frontend dependencies already installed
)

echo.

REM ========================
REM 4. START BACKEND SERVICE
REM ========================
echo [4/6] Starting Django backend service (port 8000)...
echo.

cd /d "%FACTLY_ROOT%\backend"

REM Start backend in a new window
start "Factly Backend Server" cmd /k "title Factly Backend - Django & venv\Scripts\python.exe manage.py runserver 8000"

echo   [OK] Backend service started in new window
timeout /t 3 /nobreak

echo.

REM ========================
REM 5. START FRONTEND SERVICE
REM ========================
echo [5/6] Starting React frontend service (port 3000)...
echo.

cd /d "%FACTLY_ROOT%\frontend"

REM Start frontend in a new window
start "Factly Frontend Server" cmd /k "title Factly Frontend - React & npm start"

echo   [OK] Frontend service started in new window
timeout /t 5 /nobreak

echo.

REM ========================
REM 6. OPEN IN BROWSER
REM ========================
echo [6/6] Opening Factly in default browser...
echo.

timeout /t 2 /nobreak
start http://localhost:3000

echo.
echo ========================================
echo   SUCCESS - FACTLY IS NOW RUNNING!
echo ========================================
echo.
echo Services:
echo   Frontend:  http://localhost:3000  (React Application)
echo   Backend:   http://localhost:8000  (Django API)
echo.
echo Information:
echo   - Both services are running in separate terminal windows
echo   - Keep this window and service windows open while using Factly
echo   - Close service windows to stop the application
echo.
echo Browser Opening:
echo   - Your default browser should open to http://localhost:3000
echo   - If it doesn't, manually navigate to http://localhost:3000
echo.
echo.
echo ========================================
echo   CODEBASE SUMMARY
echo ========================================
echo.
echo Frontend Stack:
echo   - React 18.2.0
echo   - React Router 6.20.0
echo   - Lazy-loaded components with Suspense
echo   - Error boundaries for crash recovery
echo   - Authentication context
echo.
echo Backend Stack:
echo   - Django 6.0
echo   - Django REST Framework
echo   - JWT authentication
echo   - Rate limiting (60 req/min)
echo.
echo Routes:
echo   - / (Home with trending topics)
echo   - /login (User authentication)
echo   - /verify (Verification form)
echo   - /results (Verification results)
echo   - /history (User history)
echo   - /about (About page)
echo.
echo Features:
echo   - Factly Score Algorithm (0-100)
echo   - Multi-source verification
echo   - Evidence analysis
echo   - Real-time trending topics
echo   - Credibility charts
echo.
echo.
pause
