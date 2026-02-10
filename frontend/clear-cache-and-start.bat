@echo off
REM Script to clear React/Webpack build cache and restart development server
REM This helps resolve ChunkLoadError issues with lazy loading and HMR

echo 🔧 Clearing build cache...

REM Remove Webpack cache
if exist "node_modules\.cache" (
    echo 📦 Removing node_modules\.cache...
    rmdir /s /q node_modules\.cache
) else (
    echo ✅ No node_modules\.cache found
)

REM Remove any temporary files
if exist "node_modules\.tmp" (
    echo 📦 Removing node_modules\.tmp...
    rmdir /s /q node_modules\.tmp
)

REM Kill any existing Node processes for this project on port 3000
echo 🛑 Checking for existing React processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo 🔴 Killing process %%a...
    taskkill /PID %%a /F 2>nul
)

echo.
echo ✅ Cache cleared successfully!
echo.
echo 🚀 To start the development server:
echo    cd frontend
echo    npm start
echo.
echo 📝 Note: If you're still experiencing ChunkLoadError after restart:
echo    1. Hard refresh the browser (Ctrl+Shift+R)
echo    2. Clear browser cache (Ctrl+Shift+Delete)
echo    3. Check browser console (F12) for network errors
echo    4. Clear localStorage in Application tab of DevTools

pause
