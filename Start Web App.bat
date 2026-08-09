@echo off
title NeuroForge Web
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Python\bin\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo  Starting NeuroForge web server...
echo  Keep this window OPEN while you play.
echo.
echo  Open in browser:  http://127.0.0.1:8080
echo.

set PORT=8080
start "" "http://127.0.0.1:8080"
"%PY%" -u -m webapp.app

echo.
echo  Server stopped.
pause
