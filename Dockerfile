# NeuroForge production image for Railway
# Start: python start.py  (also provides `gunicorn` shim on PATH)

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    WEB_CONCURRENCY=1 \
    PATH="/app/bin:/usr/local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure LF scripts + gunicorn on PATH (shell shim + pip console script)
RUN sed -i 's/\r$//' /app/bin/gunicorn /app/start.sh 2>/dev/null || true \
    && chmod +x /app/bin/gunicorn /app/start.sh \
    && cp /app/bin/gunicorn /usr/local/bin/gunicorn \
    && chmod +x /usr/local/bin/gunicorn \
    && python -c "import gunicorn, flask; print('deps-ok', gunicorn.__version__)" \
    && python -m gunicorn --version \
    && /usr/local/bin/gunicorn --version \
    && python -c "from webapp.app import app; print('build-import-ok')"

EXPOSE 8080

CMD ["python", "start.py"]
