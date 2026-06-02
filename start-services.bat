@echo off
REM Quick start script for Factly development environment
REM This script will start both backend and frontend servers

setlocal enabledelayedexpansion

echo ============================================================
echo FACTLY DEVELOPMENT ENVIRONMENT STARTUP
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: backend directory not found
    echo Please run this script from the Factly root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend directory not found
    echo Please run this script from the Factly root directory
    pause
    exit /b 1
)

echo Preparing to start services...
echo.

REM Start backend in a new window
echo Starting Backend Server (Django)...
cd backend
start "Factly Backend" cmd /k "python manage.py runserver 127.0.0.1:8000"

REM Give backend time to start
timeout /t 3 /nobreak

REM Navigate back to root
cd ..

REM Start frontend in a new window
echo Starting Frontend Server (React)...
cd frontend
start "Factly Frontend" cmd /k "npm start"

REM Navigate back to root
cd ..

echo.
echo ============================================================
echo STARTUP COMPLETE
echo ============================================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Your services should open in new windows.
echo.
echo Press any key to close this window...
pause
