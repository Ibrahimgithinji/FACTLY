# Code Quality & Deployment Workflow

## Overview
This document outlines the strict manual workflow for committing and pushing code changes to the FACTLY repository. All changes must be tested and verified locally before being pushed to the remote repository.

---

## Pre-requisites

### 1. Verify Development Servers are Running
Before making any changes, ensure both frontend and backend servers are running:

```bash
# Terminal 1 - Frontend (React)
cd frontend
npm start

# Terminal 2 - Backend (Django)
cd backend
python manage.py runserver 8000
```

### 2. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

---

## Step-by-Step Workflow for Making Changes

### Step 1: Create a Feature Branch (Recommended)
```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name
```

### Step 2: Make Your Code Changes
Edit the necessary files using your code editor.

### Step 3: Test Locally

#### A. Verify Backend Tests Pass
```bash
cd backend

# Run Django tests
python manage.py test

# Or run a specific test file
python manage.py test verification.tests.test_auth_views
```

#### B. Verify Frontend Builds
```bash
cd frontend

# Check for JavaScript errors
npm run build

# Run linting (if configured)
npm run lint
```

#### C. Manual Testing in Browser
1. Open http://localhost:3000
2. Test the specific feature you implemented
3. Verify login/logout works
4. Test the verification functionality

### Step 4: Check for Syntax Errors
```bash
# Python syntax check
python -m py_compile backend/services/your_module.py

# JavaScript syntax check (in frontend directory)
npx eslint src/your-file.js
```

---

## Commit Workflow

### Step 1: Check Git Status
```bash
git status
```

### Step 2: Stage Files
```bash
# Stage specific files
git add path/to/file1.py path/to/file2.js

# Or stage all changes
git add -A

# Stageively ( interactselect specific hunks)
git add -p
```

### Step 3: Review Staged Changes
```bash
# See what will be committed
git diff --staged
```

### Step 4: Write a Descriptive Commit Message

Follow these conventions:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance

**Example:**
```bash
git commit -m "fix(verification): resolve API key validation issue

- Add placeholder API key detection
- Add EvidenceSearchService fallback
- Improve error handling for external APIs

Fixes #123"
```

---

## Push Workflow (After Manual Verification)

### Step 1: Final Verification Checklist
Before pushing, confirm:
- [ ] All tests pass locally
- [ ] Frontend builds without errors
- [ ] Manual testing completed in browser
- [ ] No debug code left behind
- [ ] Commit message is descriptive

### Step 2: Push to Remote
```bash
# Push to origin (manual push - no automatic triggers)
git push origin main

# Or push to feature branch
git push origin feature/your-feature-name
```

### Step 3: Verify Remote Changes
1. Go to https://github.com/Ibrahimgithinji/FACTLY
2. Verify the commit appears in the repository
3. Check that the push was successful

---

## Rollback Procedure

### If Tests Fail After Push:
```bash
# Revert the last commit
git revert HEAD

# Or reset to previous commit (careful - this rewrites history)
git reset --hard HEAD~1

# Then push the revert
git push origin main
```

### If You Need to Amend a Commit:
```bash
# Modify the last commit (before pushing)
git commit --amend -m "Updated commit message"

# Force push (only if you haven't pushed yet!)
git push --force origin main
```

---

## Quality Standards

### Code Requirements
1. **No breaking changes** - Ensure backward compatibility
2. **Test coverage** - New features should have tests
3. **No secrets** - Never commit API keys or passwords
4. **Proper formatting** - Follow existing code style

### Before Every Commit
- [ ] Code compiles/runs without errors
- [ ] Manual testing in browser completed
- [ ] No console errors in browser
- [ ] No TODO comments left behind (unless intentional)
- [ ] No debug print statements

---

## Troubleshooting

### Server Not Starting
```bash
# Kill existing processes
# Windows
taskkill /F /IM python.exe

# Install dependencies
cd backend
pip install -r requirements.txt

cd frontend
npm install
```

### Database Issues
```bash
cd backend

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Git Conflicts
```bash
# Pull latest changes first
git pull origin main

# Resolve conflicts in your editor
# Then stage resolved files
git add .

# Complete the merge commit
git commit
```

---

## Summary: Quick Reference

| Action | Command |
|--------|---------|
| Check status | `git status` |
| Stage files | `git add <filename>` |
| Stage all | `git add -A` |
| Commit | `git commit -m "message"` |
| Push | `git push origin main` |
| Create branch | `git checkout -b <name>` |
| Switch branch | `git checkout <name>` |
| Pull latest | `git pull origin main` |
| View logs | `git log --oneline -10` |

---

**Remember:** Always test locally before pushing. The remote repository should only contain verified, working code.
