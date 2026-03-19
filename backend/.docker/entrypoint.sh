#!/bin/bash

# Check the value of ENV variable
if [ "$ENV" = "development" ]; then
  echo "Running in development mode with hot-reloading..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Running in production mode..."
  exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
fi