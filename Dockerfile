# Railway / any container host — reliable NeuroForge web deploy
FROM python:3.12-slim

WORKDIR /app

# System deps (none heavy needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects PORT; default 8080 matches Public Networking
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=change-me-in-railway-variables

EXPOSE 8080

# Single worker = less RAM on free tier; listen on all interfaces
CMD gunicorn -b 0.0.0.0:${PORT} -w 1 -t 120 --access-logfile - --error-logfile - webapp.app:app
