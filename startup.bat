@echo off
REM ==============================================================================
REM FACTLY - COMPLETE STARTUP SCRIPT
REM ==============================================================================
REM This script will start both the Django backend and React frontend servers,
REM run any necessary migrations, and open the application in your default browser.
REM
REM The error "500 Internal Server Error on Login" occurs when the backend
REM server is not running. This script ensures both servers are started.
REM ==============================================================================

setlocal enabledelayedexpansion

cd /d "C:\Users\DELL\OneDrive\Desktop\Factly"

echo.
echo ========================================
echo FACTLY APPLICATION STARTUP
echo ========================================
echo.

REM ==============================================================================
REM STEP 1: Run migrations
REM ==============================================================================
echo [1/4] Running Django migrations...
echo.

cd backend

echo Please wait, this may take a moment...
call venv\Scripts\python.exe manage.py migrate --noinput

if %ERRORLEVEL% EQU 0 (
    echo ✓ Migrations completed successfully
) else (
    echo ✗ Warning: Migrations may have failed, but continuing startup...
)

cd ..
echo.

REM ==============================================================================
REM STEP 2: Start Backend Server
REM ==============================================================================
echo [2/4] Starting Django backend server on port 8000...

start "Factly Backend Server" cmd /k ^
    "cd /d C:\Users\DELL\OneDrive\Desktop\Factly\backend && ^
    echo Starting backend... && ^
    venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

echo ✓ Backend started (new window should appear)
echo.

REM ==============================================================================
REM STEP 3: Wait for Backend to Initialize
REM ==============================================================================
echo [3/4] Waiting for backend to fully initialize (8 seconds)...
timeout /t 8 /nobreak

echo.

REM ==============================================================================
REM STEP 4: Start Frontend Server
REM ==============================================================================
echo [4/4] Starting React frontend server on port 3000...

start "Factly Frontend Server" cmd /k ^
    "cd /d C:\Users\DELL\OneDrive\Desktop\Factly\frontend && ^
    echo Starting frontend... && ^
    npm start"

echo ✓ Frontend started (new window should appear)
echo.

timeout /t 5 /nobreak

REM ==============================================================================
REM FINAL STEP: Open in Browser
REM ==============================================================================
echo.
echo Opening application in your default browser...
timeout /t 2 /nobreak
start http://localhost:3000

echo.
echo ========================================
echo FACTLY IS READY!
echo ========================================
echo.
echo Access Points:
echo   • Frontend:      http://localhost:3000
echo   • Backend:       http://localhost:8000
echo   • Health Check:  http://localhost:8000/health/
echo.
echo To stop the servers:
echo   • Close either terminal window with X button
echo   • Or press Ctrl+C in a terminal
echo.
echo ========================================
