# Coolify — Configuración exacta

> Error común: `open Dockerfile: no such file or directory`  
> **Causa:** Coolify busca `/Dockerfile` en la raíz. En este monorepo están en subcarpetas.

> Error común: **"Error al iniciar sesión"** en el login  
> **Causa:** El frontend no puede llegar al backend. Falta `BACKEND_INTERNAL_URL` en el servicio Frontend.

---

## Frontend (puerto 3000)

| Campo | Valor |
|-------|--------|
| Build Pack | **Dockerfile** |
| **Base Directory** | `frontend` |
| **Dockerfile Location** | `Dockerfile.prod` |
| Port | `3000` |
| Static site | No |

> **Nota:** Dockerfile Location = `Dockerfile.prod` (sin `/` al inicio). Con Base Directory `frontend`, Coolify usa `frontend/Dockerfile.prod`.

### Tiempos de build (normal)

| Deploy | Tiempo aproximado |
|--------|-------------------|
| **Primera vez** | 3–8 min (descarga deps + `next build`) |
| **Redeploy sin cambios en deps** | 1–3 min (cache de `npm ci`) |
| **Solo cambios de código** | 2–4 min (`next build`) |

Si tarda **más de 10 min**, revisá CPU/RAM del servidor en Coolify.

**Build Arguments (opcional):**

```
NEXT_PUBLIC_APP_NAME=Social AI Manager
```

**Environment Variables (runtime — obligatorio):**

```
BACKEND_INTERNAL_URL=http://<nombre-interno-del-backend>:8000
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_APP_NAME=Social AI Manager
```

### Cómo obtener BACKEND_INTERNAL_URL

1. En Coolify, abrí el servicio **Backend**
2. Copiá la **Internal URL** (ej: `http://backend-abc123:8000`)
3. Pegala en el Frontend como `BACKEND_INTERNAL_URL`

> **No uses** la URL pública del API en el frontend. El navegador llama a `/api/...` en tu dominio del frontend y Next.js reenvía al backend por la red interna de Coolify.

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

**Variables mínimas:**

```
DATABASE_URL=postgres://...        # Internal URL de PostgreSQL
REDIS_URL=redis://.../0
CELERY_BROKER_URL=redis://.../1
CELERY_RESULT_BACKEND=redis://.../2
JWT_SECRET=<generar>
ENCRYPTION_KEY=<generar>
SECRET_KEY=<generar>
FRONTEND_URL=https://app.tudominio.com
BACKEND_URL=https://api.tudominio.com
CORS_ORIGINS=https://app.tudominio.com
RUN_MIGRATIONS=true
RUN_SEED=true                      # solo la primera vez
```

Después del primer deploy exitoso con seed, cambiá `RUN_SEED=false`.

**Login demo** (si usaste seed):

- Email: `admin@example.com`
- Password: `Admin123!`

Variables completas: `scripts/coolify-output/backend.env` (generar con `setup-coolify.ps1`)

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

## Checklist login

- [ ] Backend health check OK (`/api/v1/health/ready`)
- [ ] `RUN_SEED=true` ejecutado al menos una vez
- [ ] Frontend tiene `BACKEND_INTERNAL_URL` apuntando al backend interno
- [ ] `NEXT_PUBLIC_API_URL` vacío en el frontend
- [ ] Redeploy del frontend después de cambiar variables

---

## Generar variables automáticamente

```powershell
.\scripts\setup-coolify.ps1
```

Output en `scripts/coolify-output/`
