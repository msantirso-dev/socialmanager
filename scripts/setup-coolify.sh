#!/usr/bin/env bash
# =============================================================================
# Social AI Manager — Script de configuración para Coolify
# Uso: ./scripts/setup-coolify.sh
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ""
echo "=========================================="
echo "  Social AI Manager — Setup Coolify"
echo "=========================================="
echo ""

# --- Dominios ---
read -rp "Dominio API (ej: api.tudominio.com): " API_DOMAIN
read -rp "Dominio Frontend (ej: app.tudominio.com): " APP_DOMAIN

API_URL="https://${API_DOMAIN}"
APP_URL="https://${APP_DOMAIN}"

# --- URLs internas Coolify ---
echo ""
echo "--- Recursos Coolify (Internal URLs) ---"
read -rp "PostgreSQL Internal URL (postgres://...): " DATABASE_URL
read -rp "Redis Internal URL base (redis://host:6379): " REDIS_BASE
REDIS_BASE="${REDIS_BASE%/}"
REDIS_URL="${REDIS_BASE}/0"
CELERY_BROKER_URL="${REDIS_BASE}/1"
CELERY_RESULT_BACKEND="${REDIS_BASE}/2"

# --- Secretos automáticos ---
gen_secret() { openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))"; }
gen_fernet() { python3 -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"; }

SECRET_KEY=$(gen_secret)
JWT_SECRET=$(gen_secret)
ENCRYPTION_KEY=$(gen_fernet)

echo ""
echo "Secretos generados automáticamente."

# --- Meta / IA (opcional) ---
echo ""
echo "--- Meta / Instagram (Enter para omitir) ---"
read -rp "META_APP_ID: " META_APP_ID
read -rp "META_APP_SECRET: " META_APP_SECRET

echo ""
echo "--- Proveedores IA (Enter para omitir) ---"
read -rp "OPENAI_API_KEY: " OPENAI_API_KEY
read -rp "ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
read -rp "GOOGLE_API_KEY: " GOOGLE_API_KEY

OUT_DIR="$ROOT/scripts/coolify-output"
mkdir -p "$OUT_DIR"

# --- Backend + Celery env ---
cat > "$OUT_DIR/backend.env" << EOF
# Pegar en Coolify → Backend → Environment Variables
APP_NAME=Social AI Manager
APP_ENV=production
DEBUG=false
SECRET_KEY=${SECRET_KEY}

FRONTEND_URL=${APP_URL}
BACKEND_URL=${API_URL}
API_V1_PREFIX=/api/v1

DATABASE_URL=${DATABASE_URL}
RUN_MIGRATIONS=true
RUN_SEED=false

REDIS_URL=${REDIS_URL}
CELERY_BROKER_URL=${CELERY_BROKER_URL}
CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}

JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

ENCRYPTION_KEY=${ENCRYPTION_KEY}

META_APP_ID=${META_APP_ID}
META_APP_SECRET=${META_APP_SECRET}
META_REDIRECT_URI=${API_URL}/api/v1/social/instagram/callback
META_GRAPH_API_VERSION=v21.0

OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}

CORS_ORIGINS=${APP_URL}
RATE_LIMIT_PER_MINUTE=60
EOF

# --- Celery (mismo que backend, sin RUN_MIGRATIONS en beat/worker) ---
cat > "$OUT_DIR/celery-worker.env" << EOF
# Pegar en Coolify → Celery Worker → Environment Variables
$(grep -v '^RUN_MIGRATIONS' "$OUT_DIR/backend.env" | grep -v '^RUN_SEED')
RUN_MIGRATIONS=false
EOF

cat > "$OUT_DIR/celery-beat.env" << EOF
# Pegar en Coolify → Celery Beat → Environment Variables
APP_ENV=production
DATABASE_URL=${DATABASE_URL}
CELERY_BROKER_URL=${CELERY_BROKER_URL}
CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
RUN_MIGRATIONS=false
EOF

# --- Frontend env ---
cat > "$OUT_DIR/frontend.env" << EOF
# Pegar en Coolify → Frontend → Environment Variables
NEXT_PUBLIC_API_URL=${API_URL}
NEXT_PUBLIC_APP_NAME=Social AI Manager
EOF

# --- Guía rápida servicios ---
cat > "$OUT_DIR/SERVICIOS.md" << EOF
# Configuración de servicios en Coolify

Repositorio: https://github.com/msantirso-dev/socialmanager

## Orden de creación

1. PostgreSQL 16 → DB: \`social_manager\`
2. Redis 7
3. Backend (ver abajo)
4. Celery Worker
5. Celery Beat
6. Frontend

---

## Backend

| Campo | Valor |
|-------|-------|
| Dockerfile | \`backend/Dockerfile\` |
| Port | \`8000\` |
| Domain | \`${API_DOMAIN}\` |
| Health Check | \`/api/v1/health/ready\` |
| Variables | \`scripts/coolify-output/backend.env\` |

## Celery Worker

| Campo | Valor |
|-------|-------|
| Dockerfile | \`backend/Dockerfile\` |
| Start Command | \`celery -A app.celery_app worker --loglevel=info\` |
| Variables | \`scripts/coolify-output/celery-worker.env\` |
| RUN_MIGRATIONS | \`false\` |

## Celery Beat

| Campo | Valor |
|-------|-------|
| Start Command | \`celery -A app.celery_app beat --loglevel=info\` |
| Variables | \`scripts/coolify-output/celery-beat.env\` |
| Réplicas | **1 sola** |

## Frontend

| Campo | Valor |
|-------|-------|
| Dockerfile | \`frontend/Dockerfile.prod\` |
| Port | \`3000\` |
| Domain | \`${APP_DOMAIN}\` |
| Build args | \`NEXT_PUBLIC_API_URL=${API_URL}\` |
| Variables | \`scripts/coolify-output/frontend.env\` |

## Meta Developers

Redirect URI: \`${API_URL}/api/v1/social/instagram/callback\`

## Seed demo (opcional, una vez)

En Backend temporalmente: \`RUN_SEED=true\` → redeploy → volver a \`false\`

Credenciales: \`admin@example.com\` / \`Admin123!\`
EOF

echo ""
echo "=========================================="
echo "  Archivos generados en:"
echo "  $OUT_DIR/"
echo "=========================================="
echo "  backend.env       → Backend Coolify"
echo "  celery-worker.env → Celery Worker"
echo "  celery-beat.env   → Celery Beat"
echo "  frontend.env      → Frontend"
echo "  SERVICIOS.md      → Guía paso a paso"
echo ""
echo "IMPORTANTE: Guarda backend.env en lugar seguro."
echo "Contiene secretos que no deben compartirse."
echo ""
