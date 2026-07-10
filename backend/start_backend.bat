@echo off
set ALLOW_MEMORY_DB=True
cd /d C:\Users\DELL\OneDrive\Desktop\Factly\backend
start /B venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 > backend-stdout.log 2> backend-stderr.log
