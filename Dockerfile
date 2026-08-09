# NeuroForge — Railway / Docker
# Includes a PATH shim so even a dashboard start command of
#   gunicorn -b 0.0.0.0:$PORT ...
# works (fixes: /bin/bash: line 1: gunicorn: command not found)

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    WEB_CONCURRENCY=1 \
    PATH="/app/bin:/usr/local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import gunicorn, flask; print('deps-ok', gunicorn.__version__)"

COPY . .

# Install gunicorn CLI shim onto PATH (covers bad Railway custom start commands)
RUN mkdir -p /app/bin \
    && printf '%s\n' \
        '#!/bin/sh' \
        'exec python -m gunicorn "$@"' \
        > /app/bin/gunicorn \
    && printf '%s\n' \
        '#!/bin/sh' \
        'exec python -m gunicorn "$@"' \
        > /usr/local/bin/gunicorn \
    && chmod +x /app/bin/gunicorn /usr/local/bin/gunicorn \
    && sed -i 's/\r$//' /app/bin/gunicorn /usr/local/bin/gunicorn /app/start.sh 2>/dev/null || true \
    && gunicorn --version \
    && python -c "from webapp.app import app; print('build-import-ok')"

EXPOSE 8080

# Preferred start (also set this in Railway if you use a custom command)
CMD ["python", "start.py"]
