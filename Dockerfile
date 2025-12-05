# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron tzdata && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY . .

# IMPORTANT: use correct cron file
COPY cron/2fa-cron /cron/2fa-cron
RUN chmod 0644 /cron/2fa-cron && crontab /cron/2fa-cron

VOLUME ["/data", "/cron"]

EXPOSE 8080

CMD ["bash", "-c", "cron && tail -f /var/log/cron.log & uvicorn app:app --host 0.0.0.0 --port 8080"]
