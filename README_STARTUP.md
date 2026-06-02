# Factly Startup Guide

## Quick Start

### Option 1: Automated Startup (Recommended)
Run the startup batch file:
```
startup.bat
```

This will automatically:
1. Run Django migrations
2. Start the backend server on port 8000
3. Start the frontend server on port 3000
4. Open the app in your default browser

### Option 2: Manual Startup

#### Terminal 1 - Backend Server
```cmd
cd backend
venv\Scripts\activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

#### Terminal 2 - Frontend Server
```cmd
cd frontend
npm start
```

The frontend will automatically open at http://localhost:3000

## Troubleshooting

### 500 Error on Login
**Issue**: Login fails with a 500 Internal Server Error
**Cause**: Backend server is not running
**Solution**: Ensure the backend server is running on port 8000

To check if backend is running:
- Open http://localhost:8000/health/ in your browser
- You should see a JSON response (status)

### Backend Database Issues
If you get "No writable SQLite path found":
1. Check that `C:\Users\DELL\AppData\Local\` is writable
2. Or set `ALLOW_MEMORY_DB=True` in `.env` (data won't persist across restarts)

### CORS Issues
If you get CORS errors, ensure:
- `ALLOWED_CORS=http://localhost:3000` is set in `backend/.env`
- `"proxy": "http://127.0.0.1:8000"` is set in `frontend/package.json`

## Ports

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Backend Health Check**: http://localhost:8000/health/
