#!/bin/bash

# If arguments are passed (e.g., from docker-compose command:), run them directly
if [ $# -gt 0 ]; then
  exec "$@"
fi

# Otherwise, run the web server based on ENV
if [ "$ENV" = "development" ]; then
  echo "Running in development mode with hot-reloading..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Running in production mode..."
  exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
fi
