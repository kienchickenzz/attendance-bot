#!/bin/bash

set -e

if [[ "${MIGRATION_ENABLED}" == "true" ]]; then
  echo "Running migrations"
  cd /app/server/src/database
  alembic upgrade head
fi


cd /app/server/src
exec uvicorn index:app \
    --host ${SERVER_HOST:-0.0.0.0} \
    --port ${SERVER_PORT:-8000} \
    --reload \
    --reload-dir /app/server/src \
    --log-level ${LOG_LEVEL:-debug}
