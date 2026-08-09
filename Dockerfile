# NeuroForge — Railway / Docker
# Public Networking port MUST match PORT (use 8080)

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    WEB_CONCURRENCY=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Prove the image can import the app at build time (fails the build early)
RUN python -c "from webapp.app import app; print('build-import-ok')"

EXPOSE 8080

# Pure Python entry — no shell $PORT expansion issues
CMD ["python", "start.py"]
