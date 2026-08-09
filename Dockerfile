FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint executable
RUN chmod +x /app/start.sh

# Default port — Railway Public Networking must use the same number
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# IMPORTANT: use shell so $PORT expands. Do not use bare ${PORT} without sh -c.
CMD ["/bin/sh", "/app/start.sh"]
