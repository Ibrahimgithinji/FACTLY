
#!/usr/bin/env bash
set -euo pipefail

# setup_and_run.sh
# Automate project setup and start backend + frontend dev servers.
# Run this from the repository root: `bash setup_and_run.sh`

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[FACTLY] Root: $ROOT_DIR"

cleanup() {
  echo "[FACTLY] Cleaning up background processes..."
  if [ -f "$ROOT_DIR/backend/.backend_pid" ]; then
    pid=$(cat "$ROOT_DIR/backend/.backend_pid" 2>/dev/null || echo "")
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null || true
      rm -f "$ROOT_DIR/backend/.backend_pid"
    fi
  fi
  if [ -f "$ROOT_DIR/frontend/.frontend_pid" ]; then
    pid=$(cat "$ROOT_DIR/frontend/.frontend_pid" 2>/dev/null || echo "")
    if [ -n "$pid" ]; then
      kill "$pid" 2>/dev/null || true
      rm -f "$ROOT_DIR/frontend/.frontend_pid"
    fi
  fi
}

trap cleanup EXIT

##########################
# Backend setup & run
##########################
echo "[FACTLY] Setting up backend..."
cd "$ROOT_DIR/backend"

# Create venv if missing
if [ ! -d "venv" ]; then
  echo "[FACTLY] Creating Python virtual environment..."
  python -m venv venv
fi

# Find the venv python executable (support Unix and Windows venv layout)
if [ -x "$ROOT_DIR/backend/venv/bin/python" ]; then
  VENV_PY="$ROOT_DIR/backend/venv/bin/python"
elif [ -x "$ROOT_DIR/backend/venv/Scripts/python.exe" ]; then
  VENV_PY="$ROOT_DIR/backend/venv/Scripts/python.exe"
elif [ -x "$ROOT_DIR/backend/venv/Scripts/python" ]; then
  VENV_PY="$ROOT_DIR/backend/venv/Scripts/python"
else
  echo "[WARN] venv python not found in common locations. Trying 'venv' activation fallback."
  # Try activating venv and using `python` from PATH in this shell
  if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "venv/bin/activate"
    VENV_PY="$(command -v python)"
  elif [ -f "venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source "venv/Scripts/activate"
    VENV_PY="$(command -v python)"
  else
    echo "[ERROR] Could not determine venv python. Please create a virtualenv manually."
    exit 1
  fi
fi

echo "[FACTLY] Using python: $VENV_PY"

echo "[FACTLY] Upgrading pip and installing backend requirements..."
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt

# Create .env from example if missing
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[FACTLY] Created backend/.env from backend/.env.example. Edit it with your API keys."
  else
    cat > .env <<EOF
GOOGLE_FACT_CHECK_API_KEY=your_google_api_key_here
NEWSLDR_API_KEY=your_newsldr_api_key_here
DEBUG=True
CACHE_TTL=3600
MAX_API_REQUESTS_PER_MINUTE=60
EOF
    echo "[FACTLY] Created backend/.env with placeholder values. Edit it with your API keys."
  fi
else
  echo "[FACTLY] backend/.env already exists; leaving it as-is."
fi

echo "[FACTLY] Applying Django migrations..."
"$VENV_PY" manage.py migrate

echo "[FACTLY] Starting Django dev server on port 8000 (background)..."
nohup "$VENV_PY" manage.py runserver 8000 >"$ROOT_DIR/backend/runserver.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$ROOT_DIR/backend/.backend_pid"
echo "[FACTLY] Backend PID: $BACKEND_PID (logs: $ROOT_DIR/backend/runserver.log)"

##########################
# Frontend setup & run
##########################
echo "[FACTLY] Setting up frontend..."
cd "$ROOT_DIR/frontend"

if ! command -v npm >/dev/null 2>&1; then
  echo "[ERROR] npm not found in PATH. Install Node.js and npm, then re-run this script."
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo "[FACTLY] Installing frontend dependencies (npm install)..."
  npm install
fi

echo "[FACTLY] Starting frontend dev server on port 3000 (background)..."
nohup npm start >"$ROOT_DIR/frontend/npm.log" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$ROOT_DIR/frontend/.frontend_pid"
echo "[FACTLY] Frontend PID: $FRONTEND_PID (logs: $ROOT_DIR/frontend/npm.log)"

echo "[FACTLY] All services started."
echo "Backend: http://localhost:8000  (PID $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID $FRONTEND_PID)"
echo "To stop services:"
echo "  kill \$(cat backend/.backend_pid) || echo 'failed to kill backend'"
echo "  kill \$(cat frontend/.frontend_pid) || echo 'failed to kill frontend'"
echo "Note: On Windows run the equivalent commands in PowerShell or run this script in WSL/Git Bash."
