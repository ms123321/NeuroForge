# Build NeuroForge for Android with BeeWare Briefcase
# Prerequisites: Python 3.10-3.12, Android SDK (Briefcase can prompt to install)
# Run from repo root:  .\scripts\package_android.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "=== NeuroForge Android package ===" -ForegroundColor Cyan
Write-Host "Installing briefcase + toga if needed..."
python -m pip install -q "briefcase>=0.3.19" "toga>=0.4.5"

if (-not (Test-Path "assets\icon.png")) {
    if (Test-Path "assets\icon_1024.png") {
        Copy-Item "assets\icon_1024.png" "assets\icon.png" -Force
        Write-Host "Copied icon_1024.png -> icon.png"
    }
}

Write-Host "`n[1/4] briefcase create android"
briefcase create android

Write-Host "`n[2/4] briefcase build android"
briefcase build android

Write-Host "`n[3/4] briefcase package android"
briefcase package android

Write-Host "`n[4/4] Done." -ForegroundColor Green
Write-Host "Look under build\neuroforge\android\ for APK/AAB outputs."
Write-Host "Upload the AAB to Google Play Console."
Write-Host "See MOBILE_PACKAGING.md for store listing + pricing."
