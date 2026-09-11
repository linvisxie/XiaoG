@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title XiaoG

if not exist ".venv\Scripts\python.exe" (
  echo XiaoG has not been set up yet.
  echo Please double-click setup_windows.bat first.
  pause
  exit /b 1
)

echo Starting XiaoG at http://127.0.0.1:8000 ...
start "XiaoG Backend" /B ".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

set "READY="
for /L %%i in (1,1,20) do (
  powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 http://127.0.0.1:8000/health; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 set "READY=1"& goto :open_browser
  timeout /t 1 /nobreak >nul
)

echo XiaoG did not start within 20 seconds.
echo Check data\logs\xiaog.log for a developer log.
pause
exit /b 1

:open_browser
start "" "http://127.0.0.1:8000"
echo XiaoG is running. Keep this window open while using it.
echo To stop it, close this window.
pause
