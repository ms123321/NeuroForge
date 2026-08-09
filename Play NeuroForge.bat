@echo off
title NeuroForge
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Python\bin\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo  Starting NeuroForge...
echo  A dark blue window should appear on your screen.
echo  Keep this black console open while you play.
echo  Close the game window (X) when you are done.
echo.

"%PY%" -u main.py
if errorlevel 1 (
  echo.
  echo  GAME CRASHED — error above.
  pause
  exit /b 1
)

echo.
echo  Game closed.
pause
