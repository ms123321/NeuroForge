# NeuroForge — Railway / Docker (Waitress, no gunicorn)
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import flask, waitress; print('deps-ok')"

COPY . .

RUN python -c "from webapp.app import app; print('build-import-ok')"

EXPOSE 8080

CMD ["python", "start.py"]
