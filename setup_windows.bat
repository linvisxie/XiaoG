@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title XiaoG Setup

echo.
echo ==========================================
echo              XiaoG v0.1 Setup
echo ==========================================
echo Project folder: %CD%
echo.

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>nul && set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
  echo [ERROR] Python was not found.
  echo Please install Python 3.11 or newer from https://www.python.org/downloads/windows/
  echo During installation, tick "Add python.exe to PATH".
  echo Then close this window and double-click setup_windows.bat again.
  pause
  exit /b 1
)

echo [1/6] Checking Python...
%PYTHON_CMD% --version || goto :python_error

echo [2/6] Creating local virtual environment: D:\XiaoG\.venv
if not exist ".venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .venv || goto :failed
)

echo [3/6] Updating installer tools...
".venv\Scripts\python.exe" -m pip install --upgrade pip || goto :failed

echo [4/6] Installing XiaoG dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :failed

echo [5/6] Creating local .env if needed...
if not exist ".env" copy /Y ".env.example" ".env" >nul

echo [6/6] Initializing SQLite database...
".venv\Scripts\python.exe" -c "from backend.database.db import initialize_database; initialize_database(); print('SQLite database ready: data\\xiaog.db')" || goto :failed

echo.
where codex >nul 2>nul
if errorlevel 1 (
  echo [Info] Codex CLI is not installed or not on PATH. This is OK for XiaoG v0.1.
  echo        Phase 3 will check it before adding GPT-5.6 Terra through the official App Server.
) else (
  echo [Info] Codex CLI found. Phase 3 will verify its official App Server and your actual model list.
)
echo.
echo Setup complete.
echo Next: open .env in this folder and fill DEEPSEEK_API_KEY=your_key
echo Then double-click run_windows.bat.
pause
exit /b 0

:python_error
echo [ERROR] Python could not run correctly.
pause
exit /b 1

:failed
echo.
echo [ERROR] Setup did not finish. Read the message above, then run this file again.
pause
exit /b 1
