#!/usr/bin/env bash
# =============================================================================
# Social AI Manager — Setup local con Docker Compose
# Uso: ./scripts/setup-local.sh
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Social AI Manager — Setup local"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Creado .env desde .env.example"
fi

gen_secret() { openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))"; }
gen_fernet() { python3 -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"; }

# Reemplazar secretos placeholder en .env
if grep -q "change-me" .env 2>/dev/null; then
  SECRET=$(gen_secret)
  JWT=$(gen_secret)
  FERNET=$(gen_fernet)
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=${SECRET}/" .env
    sed -i '' "s/JWT_SECRET=.*/JWT_SECRET=${JWT}/" .env
    sed -i '' "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=${FERNET}/" .env
  else
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET}/" .env
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=${JWT}/" .env
    sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=${FERNET}/" .env
  fi
  echo "Secretos generados en .env"
fi

echo "Levantando Docker Compose..."
docker compose up -d --build

echo ""
echo "Esperando servicios..."
sleep 15

echo ""
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "Swagger:   http://localhost:8000/docs"
echo ""
echo "Seed demo (opcional):"
echo "  RUN_SEED=true docker compose up -d backend"
echo ""
echo "Login: admin@example.com / Admin123!"
