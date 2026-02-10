#!/bin/bash

# Script to clear React/Webpack build cache and restart development server
# This helps resolve ChunkLoadError issues with lazy loading and HMR

echo "🔧 Clearing build cache..."

# Remove Webpack cache
if [ -d "node_modules/.cache" ]; then
  echo "📦 Removing node_modules/.cache..."
  rm -rf node_modules/.cache
else
  echo "✅ No node_modules/.cache found"
fi

# Remove any temporary files
if [ -d "node_modules/.tmp" ]; then
  echo "📦 Removing node_modules/.tmp..."
  rm -rf node_modules/.tmp
fi

# Clear localStorage (user will need to do this manually in browser devtools)
echo "🧹 To clear localStorage:"
echo "   1. Open browser DevTools (F12)"
echo "   2. Go to Application > Local Storage"
echo "   3. Right-click and clear all"

# Kill any existing Node processes for this project
echo "🛑 Checking for existing React processes..."
if command -v lsof &> /dev/null; then
  lsof -ti:3000 | xargs kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
  netstat -ano | findstr :3000 | FOR /F "tokens=5" %%a in ('findstr :3000') do taskkill /PID %%a /F 2>nul || true
else
  echo "⚠️  Could not detect process killer. Please manually stop any running React dev server."
fi

echo ""
echo "✅ Cache cleared successfully!"
echo ""
echo "🚀 To start the development server:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "📝 Note: If you're still experiencing ChunkLoadError after restart:"
echo "   1. Hard refresh the browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   2. Clear browser cache"
echo "   3. Check browser console for network errors"
