#!/bin/bash
# Force push all necessary project files to GitHub

echo "[FACTLY] Ensuring all source files are tracked..."

cd "$(dirname "$0")"

# Add all source files explicitly
echo "Adding backend source files..."
git add backend/*.py
git add backend/*.txt
git add backend/*.sh
git add backend/factly_backend/
git add backend/services/
git add backend/verification/
git add backend/.env.example

echo "Adding frontend source files..."
git add frontend/src/
git add frontend/public/
git add frontend/package.json
git add frontend/package-lock.json

echo "Adding root configuration files..."
git add README.md
git add LICENSE
git add CONTRIBUTING.md
git add GIT_READINESS.md
git add setup_and_run.sh
git add .gitignore
git add .gitattributes

echo "Current git status:"
git status

echo ""
echo "Files to be committed:"
git diff --cached --name-only

echo ""
read -p "Push these files to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Committing and pushing..."
    git commit -m "fix: push all source files to repository"
    git push -u origin main
    echo "✓ Push complete!"
else
    echo "Push cancelled."
fi
