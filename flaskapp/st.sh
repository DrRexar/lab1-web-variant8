#!/usr/bin/env bash
gunicorn --bind 127.0.0.1:5000 wsgi:app &
APP_PID=$!

sleep 5
echo "=== start client ==="
python3 client.py
APP_CODE=$?

sleep 2
kill -TERM "$APP_PID" 2>/dev/null || true
wait "$APP_PID" 2>/dev/null || true

echo "=== app code: $APP_CODE ==="
exit $APP_CODE