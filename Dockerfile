FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/start.sh \
    && sed -i 's/\r$//' /app/start.sh

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV WEB_CONCURRENCY=1

EXPOSE 8080

# Shell entrypoint so PORT is always expanded
CMD ["/bin/sh", "/app/start.sh"]
