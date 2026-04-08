@echo off
REM Start Factly Application - Backend and Frontend
REM This script will start both the Django backend and React frontend

cd /d c:\Users\DELL\OneDrive\Desktop\Factly

echo ========================================
echo Starting Factly Application...
echo ========================================

REM Start Backend Django Server in a new window
echo.
echo [1/2] Starting Django backend server on port 8000...
start "Factly Backend" cmd /k "cd backend && venv\Scripts\python.exe manage.py runserver 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start Frontend React Server in a new window
echo [2/2] Starting React frontend server on port 3000...
start "Factly Frontend" cmd /k "cd frontend && npm start"

REM Wait for frontend to start
timeout /t 5 /nobreak

REM Open in default browser
echo.
echo Opening Factly in default browser...
timeout /t 3 /nobreak
start http://localhost:3000

echo.
echo ========================================
echo Factly is starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ========================================
