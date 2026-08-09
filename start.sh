#!/bin/sh
# Fallback only — prefer `python start.py` (no bare gunicorn binary)
set -eu
export PORT="${PORT:-8080}"
export PYTHONUNBUFFERED=1
echo "start.sh → python start.py (PORT=${PORT})"
exec python start.py
