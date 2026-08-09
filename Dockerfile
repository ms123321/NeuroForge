# NeuroForge — Railway / Docker
# Never rely on `gunicorn` being on PATH — use `python start.py`

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    WEB_CONCURRENCY=1 \
    PATH="/usr/local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import gunicorn, flask; print('deps-ok', gunicorn.__version__, flask.__version__)"

COPY . .

# Build-time smoke test
RUN python -c "from webapp.app import app; print('build-import-ok')"

EXPOSE 8080

# Module entry — works even if gunicorn binary is not on PATH
CMD ["python", "start.py"]
