@echo off
echo Starting PhishGuard Backend API...
cd apps\backend
python -m uvicorn app.main:app --reload --port 8000
