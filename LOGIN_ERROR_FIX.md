# Fix: 500 Internal Server Error on Login

## Problem
User encountered a 500 Internal Server Error when attempting to login:
```
AuthContext.js:281 Login error: Error: Server error: 500 Internal Server Error
```

## Root Cause
The **Django backend server was not running** on port 8000. 

When the frontend (running on port 3000) tried to communicate with the backend API endpoint `/api/verification/auth/login/`, the request failed because there was no server listening on port 8000.

## Solution Applied

### 1. Enabled In-Memory Database Fallback
Updated `backend/.env` to allow the backend to use an in-memory SQLite database as a fallback:

```env
ALLOW_MEMORY_DB=True
STRICT_SQLITE_PATH=False
```

This ensures the backend can start even if the configured database path (`C:\Users\DELL\AppData\Local\factly-db.sqlite3`) is not accessible.

### 2. How to Start the Application

#### Quick Start (Recommended)
```bash
startup.bat
```

This script will:
- Run Django migrations
- Start the backend server on port 8000
- Start the frontend server on port 3000
- Open the application in your default browser

#### Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 3. Verify the Fix
- Backend should be running at: http://localhost:8000
- Frontend should be running at: http://localhost:3000
- Health check endpoint: http://localhost:8000/health/

## How It Works

### Frontend to Backend Communication
The frontend (`package.json`) has a proxy configured:
```json
"proxy": "http://127.0.0.1:8000"
```

This means when the frontend makes a request to `/api/verification/auth/login/`, it automatically proxies it to `http://127.0.0.1:8000/api/verification/auth/login/`.

### API Endpoint Configuration
The login endpoint is defined in `backend/verification/urls.py`:
```python
path('verification/auth/login/', auth_views.LoginView.as_view(), name='login')
```

And called from the frontend via `frontend/src/utils/api.js`:
```javascript
LOGIN: `${API_BASE_URL}/api/verification/auth/login/`
```

### Database Initialization
The backend automatically:
1. Checks if the database path is writable
2. Falls back to `C:\Users\DELL\AppData\Local\factly-db.sqlite3` if the configured path fails
3. Falls back to in-memory database (`:memory:`) if disk paths fail
4. Automatically runs migrations on first login attempt (see `auth_views.py` line 144)

## Key Files Modified
- `backend/.env` - Added `ALLOW_MEMORY_DB=True` and improved comments
- `startup.bat` - Created automated startup script
- `start-backend.bat` - Created backend-only startup script
- `README_STARTUP.md` - Created startup guide

## Important Notes

⚠️ **In-Memory Database Warning**
When using `ALLOW_MEMORY_DB=True`, all data is stored in memory and will be **LOST** when the backend server restarts. This is only recommended for development and testing.

For persistent data, ensure:
1. `C:\Users\DELL\AppData\Local\` exists and is writable
2. Or configure a different database path via `SQLITE_DB_PATH` in `.env`
3. Or use a real database (PostgreSQL, MySQL) in production

## Testing the Login
1. Run `startup.bat` or manually start both servers
2. Open http://localhost:3000 in your browser
3. Try to login or signup
4. The request should now reach the backend server and process correctly

If you still get a 500 error:
1. Check the backend console for detailed error messages
2. Check `backend/factly.log` for server logs
3. Verify the backend is running on port 8000 by visiting http://localhost:8000/health/

## Future Improvements
- [ ] Set up persistent SQLite database in a non-OneDrive location
- [ ] Configure PostgreSQL for production use
- [ ] Set up Redis for Celery task queue (currently depends on it)
- [ ] Configure proper email backend for password reset
