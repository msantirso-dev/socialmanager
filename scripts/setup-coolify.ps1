# =============================================================================
# Social AI Manager — Script de configuración para Coolify (Windows)
# Uso: .\scripts\setup-coolify.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Social AI Manager — Setup Coolify" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function New-RandomHex {
    -join ((1..64) | ForEach-Object { "{0:x}" -f (Get-Random -Maximum 16) })
}

function New-FernetKey {
    $bytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    [Convert]::ToBase64String($bytes)
}

# --- Dominios ---
$ApiDomain = Read-Host "Dominio API (ej: api.tudominio.com)"
$AppDomain = Read-Host "Dominio Frontend (ej: app.tudominio.com)"

$ApiUrl = "https://$ApiDomain"
$AppUrl = "https://$AppDomain"

# --- URLs internas Coolify ---
Write-Host ""
Write-Host "--- Recursos Coolify (Internal URLs) ---" -ForegroundColor Yellow
$DatabaseUrl = Read-Host "PostgreSQL Internal URL (postgres://...)"
$RedisBase = Read-Host "Redis Internal URL base (redis://host:6379)"
$RedisBase = $RedisBase.TrimEnd('/')
$RedisUrl = "$RedisBase/0"
$CeleryBroker = "$RedisBase/1"
$CeleryBackend = "$RedisBase/2"
$BackendInternalUrl = Read-Host "Backend Internal URL para el Frontend (ej: http://backend-xxx:8000)"

# --- Secretos ---
$SecretKey = New-RandomHex
$JwtSecret = New-RandomHex
$EncryptionKey = New-FernetKey

Write-Host ""
Write-Host "Secretos generados automaticamente." -ForegroundColor Green

# --- Meta / IA ---
Write-Host ""
Write-Host "--- Meta / Instagram (Enter para omitir) ---" -ForegroundColor Yellow
$MetaAppId = Read-Host "META_APP_ID"
$MetaAppSecret = Read-Host "META_APP_SECRET"

Write-Host ""
Write-Host "--- Proveedores IA (Enter para omitir) ---" -ForegroundColor Yellow
$OpenAiKey = Read-Host "OPENAI_API_KEY"
$AnthropicKey = Read-Host "ANTHROPIC_API_KEY"
$GoogleKey = Read-Host "GOOGLE_API_KEY"

$OutDir = Join-Path $Root "scripts\coolify-output"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# --- Backend env ---
$BackendEnv = @"
# Pegar en Coolify -> Backend -> Environment Variables
APP_NAME=Social AI Manager
APP_ENV=production
DEBUG=false
SECRET_KEY=$SecretKey

FRONTEND_URL=$AppUrl
BACKEND_URL=$ApiUrl
API_V1_PREFIX=/api/v1

DATABASE_URL=$DatabaseUrl
RUN_MIGRATIONS=true
RUN_SEED=false

REDIS_URL=$RedisUrl
CELERY_BROKER_URL=$CeleryBroker
CELERY_RESULT_BACKEND=$CeleryBackend

JWT_SECRET=$JwtSecret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

ENCRYPTION_KEY=$EncryptionKey

META_APP_ID=$MetaAppId
META_APP_SECRET=$MetaAppSecret
META_REDIRECT_URI=$ApiUrl/api/v1/social/instagram/callback
META_GRAPH_API_VERSION=v21.0

OPENAI_API_KEY=$OpenAiKey
ANTHROPIC_API_KEY=$AnthropicKey
GOOGLE_API_KEY=$GoogleKey

CORS_ORIGINS=$AppUrl
RATE_LIMIT_PER_MINUTE=60
"@

$BackendEnv | Out-File -FilePath (Join-Path $OutDir "backend.env") -Encoding utf8NoBOM

# --- Celery worker ---
$CeleryWorkerEnv = ($BackendEnv -replace "RUN_MIGRATIONS=true", "RUN_MIGRATIONS=false") -replace "RUN_SEED=false`r?`n", ""
$CeleryWorkerEnv | Out-File -FilePath (Join-Path $OutDir "celery-worker.env") -Encoding utf8NoBOM

# --- Celery beat ---
$CeleryBeatEnv = @"
APP_ENV=production
DATABASE_URL=$DatabaseUrl
CELERY_BROKER_URL=$CeleryBroker
CELERY_RESULT_BACKEND=$CeleryBackend
RUN_MIGRATIONS=false
"@
$CeleryBeatEnv | Out-File -FilePath (Join-Path $OutDir "celery-beat.env") -Encoding utf8NoBOM

# --- Frontend ---
$FrontendEnv = @"
# Pegar en Coolify -> Frontend -> Environment Variables
BACKEND_INTERNAL_URL=$BackendInternalUrl
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_APP_NAME=Social AI Manager
"@
$FrontendEnv | Out-File -FilePath (Join-Path $OutDir "frontend.env") -Encoding utf8NoBOM

# --- Guía servicios ---
$ServiciosMd = @"
# Configuracion de servicios en Coolify

Repositorio: https://github.com/msantirso-dev/socialmanager

## Orden de creacion

1. PostgreSQL 16 -> DB: ``social_manager``
2. Redis 7
3. Backend
4. Celery Worker
5. Celery Beat
6. Frontend

---

## Backend

| Campo | Valor |
|-------|-------|
| Dockerfile | ``backend/Dockerfile`` |
| Port | ``8000`` |
| Domain | ``$ApiDomain`` |
| Health Check | ``/api/v1/health/ready`` |
| Variables | ``scripts/coolify-output/backend.env`` |

## Celery Worker

| Campo | Valor |
|-------|-------|
| Dockerfile | ``backend/Dockerfile`` |
| Start Command | ``celery -A app.celery_app worker --loglevel=info`` |
| Variables | ``scripts/coolify-output/celery-worker.env`` |

## Celery Beat

| Campo | Valor |
|-------|-------|
| Start Command | ``celery -A app.celery_app beat --loglevel=info`` |
| Variables | ``scripts/coolify-output/celery-beat.env`` |
| Replicas | **1 sola** |

## Frontend

| Campo | Valor |
|-------|-------|
| Dockerfile | ``frontend/Dockerfile.prod`` |
| Port | ``3000`` |
| Domain | ``$AppDomain`` |
| Variables | ``scripts/coolify-output/frontend.env`` |
| Importante | ``BACKEND_INTERNAL_URL=$BackendInternalUrl`` |

## Meta Developers

Redirect URI: ``$ApiUrl/api/v1/social/instagram/callback``

## Seed demo (opcional)

Backend temporalmente: ``RUN_SEED=true`` -> redeploy -> ``false``

Credenciales: ``admin@example.com`` / ``Admin123!``
"@
$ServiciosMd | Out-File -FilePath (Join-Path $OutDir "SERVICIOS.md") -Encoding utf8NoBOM

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Archivos generados en:" -ForegroundColor Green
Write-Host "  $OutDir" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  backend.env       -> Backend Coolify"
Write-Host "  celery-worker.env -> Celery Worker"
Write-Host "  celery-beat.env   -> Celery Beat"
Write-Host "  frontend.env      -> Frontend"
Write-Host "  SERVICIOS.md      -> Guia paso a paso"
Write-Host ""
Write-Host "IMPORTANTE: Guarda backend.env en lugar seguro." -ForegroundColor Yellow
Write-Host ""
