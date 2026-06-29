#!/bin/sh
set -e

echo "[entrypoint] Social AI Manager backend starting..."

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "[entrypoint] Running Alembic migrations..."
  alembic upgrade head
  echo "[entrypoint] Migrations complete."
fi

if [ "$RUN_SEED" = "true" ]; then
  echo "[entrypoint] Running database seed..."
  python -m app.scripts.seed
  echo "[entrypoint] Seed complete."
fi

exec "$@"
