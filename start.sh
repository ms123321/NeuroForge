#!/bin/sh
# Railway entrypoint — bind immediately on PORT (default 8080)
set -eu

PORT="${PORT:-8080}"
export PORT
export PYTHONUNBUFFERED=1

echo "========================================"
echo " NeuroForge boot"
echo " PORT=${PORT}"
echo " PWD=$(pwd)"
echo " Python=$(python --version 2>&1)"
echo "========================================"

# Fast path: start gunicorn without a separate pre-import process
# (pre-import doubled boot time and could race the healthcheck)
exec gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level info \
  webapp.app:app
