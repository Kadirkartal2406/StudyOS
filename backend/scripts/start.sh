#!/bin/sh
set -e
cd /app
echo "Running alembic upgrade head..."
alembic upgrade head
echo "Starting uvicorn on 0.0.0.0:${PORT:-8002}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8002}" --proxy-headers --forwarded-allow-ips='*'
