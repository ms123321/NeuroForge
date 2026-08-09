@echo off
title NeuroForge Backup
cd /d "%~dp0"

echo.
echo  Creating backup of NeuroForge + your progress...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\backup_everything.ps1"

echo.
if errorlevel 1 (
  echo  Backup failed.
) else (
  echo  Done. Check the "backups" folder.
)
echo.
pause
