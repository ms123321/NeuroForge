#!/bin/sh
# Railway / Docker entrypoint — always bind to PORT (default 8080)
set -e

export PORT="${PORT:-8080}"
export PYTHONUNBUFFERED=1

echo "NeuroForge starting on 0.0.0.0:${PORT}"
echo "Python: $(python --version 2>&1)"
echo "PWD: $(pwd)"

# Prove the app imports before gunicorn (shows errors in Railway logs)
python -c "from webapp.app import app; print('Flask app import OK', flush=True)"

exec gunicorn \
  -b "0.0.0.0:${PORT}" \
  -w 1 \
  -t 120 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  webapp.app:app
