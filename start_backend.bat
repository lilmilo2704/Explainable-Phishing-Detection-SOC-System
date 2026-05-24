@echo off
setlocal
echo Starting PhishGuard Backend API...
cd /d "%~dp0"
if exist "secrets\gmail\credentials.json" if exist "secrets\gmail\token.json" (
  echo Detected ignored local Gmail credential/token files for manual sync.
)
cd apps\backend
python -m uvicorn app.main:app --reload --port 8000
