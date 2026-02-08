#!/bin/bash
# Clean repository and fix git tracking issues
# This script removes node_modules from git, resets staging, and does a clean push

set -e

echo "================================"
echo "FACTLY Repository Cleanup"
echo "================================"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Checking current status..."
echo "Current branch and commits:"
git log --oneline | head -5
echo ""

echo "[2/5] Removing node_modules from git tracking..."
# Remove node_modules from git without deleting local files
git rm -r --cached frontend/node_modules/ 2>/dev/null || echo "  ℹ node_modules not in git index"

echo ""
echo "[3/5] Resetting staging area..."
git reset HEAD

echo ""
echo "[4/5] Adding proper files..."

# Add backend
echo "  Adding backend source code..."
git add backend/manage.py
git add backend/requirements.txt
git add backend/.env.example
git add backend/factly_backend/
git add backend/services/
git add backend/verification/

# Add frontend (excluding node_modules)
echo "  Adding frontend source code..."
git add frontend/src/
git add frontend/public/
git add frontend/package.json
git add frontend/package-lock.json

# Add root files
echo "  Adding configuration and documentation..."
git add README.md
git add LICENSE
git add CONTRIBUTING.md
git add GIT_READINESS.md
git add FIX_PUSH_GUIDE.md
git add setup_and_run.sh
git add fix-push.sh
git add .gitignore
git add .gitattributes

echo ""
echo "[5/5] Verifying staged files..."
echo ""
echo "Files staged for commit:"
git diff --cached --name-only | sort

echo ""
echo "================================"
echo "Summary:"
echo "================================"
STAGED_COUNT=$(git diff --cached --name-only | wc -l)
echo "✓ Total files staged: $STAGED_COUNT"
echo ""

echo "Next steps:"
echo "1. Review files: git status"
echo "2. Commit: git commit -m 'feat: add complete source code (backend and frontend)'"
echo "3. Push: git push origin main --force-with-lease"
echo ""
echo "Or run: git commit -m 'feat: add complete source code' && git push origin main --force-with-lease"
