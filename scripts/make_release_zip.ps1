# Create a source release zip for handoff / CI (not a signed store binary)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$stamp = Get-Date -Format "yyyyMMdd"
$out = Join-Path $root "dist"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$zip = Join-Path $out "NeuroForge-mobile-source-$stamp.zip"

if (Test-Path $zip) { Remove-Item $zip -Force }

# Compress project without caches / build artifacts
$temp = Join-Path $env:TEMP "neuroforge_pack_$stamp"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
New-Item -ItemType Directory -Force -Path $temp | Out-Null

$exclude = @("__pycache__", ".git", "build", "dist", "*.pyc", ".briefcase")
robocopy $root $temp /E /XD __pycache__ .git build dist .briefcase /XF *.pyc /NFL /NDL /NJH /NJS | Out-Null

Compress-Archive -Path (Join-Path $temp "*") -DestinationPath $zip -Force
Remove-Item $temp -Recurse -Force

Write-Host "Created: $zip"
Write-Host "Size: $([math]::Round((Get-Item $zip).Length / 1MB, 2)) MB"
Write-Host "This is SOURCE for Briefcase builds - not a signed .ipa/.aab."
