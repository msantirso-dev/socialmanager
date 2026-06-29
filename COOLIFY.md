# Coolify — Configuración exacta

> Error común: `open Dockerfile: no such file or directory`  
> **Causa:** Coolify busca `/Dockerfile` en la raíz. En este monorepo están en subcarpetas.

---

## Frontend (puerto 3000)

| Campo | Valor |
|-------|--------|
| Build Pack | **Dockerfile** |
| **Base Directory** | `frontend` |
| **Dockerfile Location** | `Dockerfile.prod` |
| Port | `3000` |
| Static site | No |

**Build Arguments:**

```
NEXT_PUBLIC_API_URL=https://api.tudominio.com
NEXT_PUBLIC_APP_NAME=Social AI Manager
```

**Environment Variables:** igual que build args + ver `scripts/coolify-output/frontend.env`

**Domain:** `app.tudominio.com`

---

## Backend (puerto 8000)

| Campo | Valor |
|-------|--------|
| Build Pack | **Dockerfile** |
| **Base Directory** | `backend` |
| **Dockerfile Location** | `Dockerfile` |
| Port | `8000` |
| Health Check Path | `/api/v1/health/ready` |

Variables: `scripts/coolify-output/backend.env` (generar con `setup-coolify.ps1`)

---

## Celery Worker

| Campo | Valor |
|-------|--------|
| Base Directory | `backend` |
| Dockerfile | `Dockerfile` |
| **Start Command** | `celery -A app.celery_app worker --loglevel=info` |
| Port | *(ninguno / no exponer)* |

Variables: `celery-worker.env`

---

## Celery Beat

| Campo | Valor |
|-------|--------|
| Base Directory | `backend` |
| Dockerfile | `Dockerfile` |
| **Start Command** | `celery -A app.celery_app beat --loglevel=info` |
| Réplicas | **1** |

Variables: `celery-beat.env`

---

## Recursos previos (obligatorios)

1. **PostgreSQL 16** → database: `social_manager`
2. **Redis 7**

Sin estos dos, el health check del backend fallará.

---

## Orden de deploy

```
PostgreSQL → Redis → Backend → Celery Worker → Celery Beat → Frontend
```

---

## Generar variables automáticamente

```powershell
.\scripts\setup-coolify.ps1
```

Output en `scripts/coolify-output/`
