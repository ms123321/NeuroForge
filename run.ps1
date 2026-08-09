# Launch NeuroForge
$py = "$env:LOCALAPPDATA\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
Set-Location $PSScriptRoot
& $py main.py
