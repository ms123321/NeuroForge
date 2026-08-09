# Backup NeuroForge project + your game progress/entitlement
# Double-click or run:  .\scripts\backup_everything.ps1

$ErrorActionPreference = "Stop"
$project = Split-Path $PSScriptRoot -Parent
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$outDir = Join-Path $project "backups"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$zip = Join-Path $outDir "NeuroForge_backup_$stamp.zip"
$temp = Join-Path $env:TEMP "nf_backup_$stamp"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
New-Item -ItemType Directory -Force -Path $temp | Out-Null

# Project (skip heavy caches)
robocopy $project (Join-Path $temp "NeuroForge") /E `
  /XD __pycache__ .git build dist .briefcase backups .venv venv `
  /XF *.pyc /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null

# Player data
$data = Join-Path $env:LOCALAPPDATA "NeuroForge"
if (Test-Path $data) {
  robocopy $data (Join-Path $temp "PlayerData") /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
}

Compress-Archive -Path (Join-Path $temp "*") -DestinationPath $zip -Force
Remove-Item $temp -Recurse -Force

Write-Host ""
Write-Host "Backup saved:" -ForegroundColor Green
Write-Host "  $zip"
Write-Host "Size: $([math]::Round((Get-Item $zip).Length/1MB, 2)) MB"
Write-Host ""
Write-Host "Includes:"
Write-Host "  - Full game source code"
Write-Host "  - progress.json (scores, levels, streaks)"
Write-Host "  - entitlement.json (Free/Pro plan)"
Write-Host ""
Write-Host "To restore progress later, copy PlayerData\* to:"
Write-Host "  $env:LOCALAPPDATA\NeuroForge\"
