# Despliegue en Coolify — Social AI Manager

Guía de producción optimizada para **Coolify**. La base de datos usa migraciones automáticas al arrancar el backend.

---

## Arquitectura en Coolify

```
                         ┌──────────────────┐
                         │ Coolify (Traefik)│
                         └────────┬─────────┘
                                  │ HTTPS
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
    ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
    │  Frontend   │        │   Backend   │        │   Celery    │
    │  Next.js    │        │   FastAPI   │        │ Worker+Beat │
    │  :3000      │        │   :8000     │        │  (interno)  │
    └─────────────┘        └──────┬──────┘        └──────┬──────┘
                                  │                      │
                    ┌─────────────┴─────────────┐        │
                    ▼                           ▼        │
            ┌───────────────┐           ┌───────────────┐  │
            │  PostgreSQL   │           │    Redis      │◄─┘
            │  (recurso)    │           │  (recurso)    │
            └───────────────┘           └───────────────┘
```

**Orden de despliegue recomendado:** PostgreSQL → Redis → Backend → Celery Worker → Celery Beat → Frontend

---

## 1. PostgreSQL (recurso Coolify)

1. **+ New Resource** → **Database** → **PostgreSQL 16**
2. Nombre: `sam-postgres`
3. Database name: `social_manager`
4. Copiar la **Internal URL** (ej: `postgres://user:pass@postgresql-abc:5432/social_manager`)

> El backend normaliza automáticamente `postgres://` → `postgresql+asyncpg://`. Pega la URL tal como Coolify la entrega.

---

## 2. Redis (recurso Coolify)

1. **+ New Resource** → **Database** → **Redis 7**
2. Copiar **Internal URL** (ej: `redis://redis-abc:6379`)

Configurar en variables del backend:

```env
REDIS_URL=redis://redis-abc:6379/0
CELERY_BROKER_URL=redis://redis-abc:6379/1
CELERY_RESULT_BACKEND=redis://redis-abc:6379/2
```

---

## 3. Backend (aplicación principal)

| Campo | Valor |
|-------|-------|
| Build Pack | Dockerfile |
| Dockerfile location | `backend/Dockerfile` |
| Port | `8000` |
| Domain | `api.tudominio.com` |
| Health Check Path | `/api/v1/health/ready` |
| Health Check Port | `8000` |

### Variables de entorno obligatorias

```env
APP_ENV=production
DEBUG=false

# Coolify: pegar Internal URL del PostgreSQL
DATABASE_URL=postgres://user:pass@postgresql-xxx:5432/social_manager

# Migraciones automáticas al deploy (recomendado)
RUN_MIGRATIONS=true
RUN_SEED=false

# Redis (URLs internas de Coolify)
REDIS_URL=redis://redis-xxx:6379/0
CELERY_BROKER_URL=redis://redis-xxx:6379/1
CELERY_RESULT_BACKEND=redis://redis-xxx:6379/2

# Seguridad — generar valores únicos
SECRET_KEY=<64-chars-random>
JWT_SECRET=<64-chars-random>
ENCRYPTION_KEY=<32-bytes-base64>

# URLs públicas
FRONTEND_URL=https://app.tudominio.com
BACKEND_URL=https://api.tudominio.com
CORS_ORIGINS=https://app.tudominio.com

# Meta / Instagram
META_APP_ID=...
META_APP_SECRET=...
META_REDIRECT_URI=https://api.tudominio.com/api/v1/social/instagram/callback
META_GRAPH_API_VERSION=v21.0

# IA (según proveedores que uses)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

### Migraciones automáticas

El `entrypoint.sh` del backend ejecuta `alembic upgrade head` cuando `RUN_MIGRATIONS=true`.

Flujo en cada deploy de Coolify:

1. Coolify construye la imagen
2. Arranca el contenedor
3. Entrypoint aplica migraciones pendientes
4. Inicia Uvicorn

**No necesitas entrar al contenedor manualmente** salvo en casos excepcionales.

### Health check para Coolify

El endpoint `/api/v1/health/ready` verifica:

- Conexión PostgreSQL
- Conexión Redis
- Migraciones aplicadas (`alembic_version` presente)
- Conteo de tablas

Respuesta esperada:

```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true,
    "migrations": true,
    "alembic_version": "f5d5a32a2f19",
    "database_tables": 18
  }
}
```

Coolify marcará el servicio como healthy solo cuando los tres checks críticos sean `true`.

---

## 4. Celery Worker

Duplicar el servicio backend con estos cambios:

| Campo | Valor |
|-------|-------|
| Dockerfile | `backend/Dockerfile` |
| Start Command | `celery -A app.celery_app worker --loglevel=info` |
| Domain | *(ninguno — servicio interno)* |
| RUN_MIGRATIONS | `false` |

Mismas variables de entorno que el backend (DATABASE_URL, REDIS, etc.).

---

## 5. Celery Beat (scheduler)

| Campo | Valor |
|-------|-------|
| Start Command | `celery -A app.celery_app beat --loglevel=info` |
| RUN_MIGRATIONS | `false` |
| Réplicas | **1 única instancia** (nunca escalar Beat) |

---

## 6. Frontend

| Campo | Valor |
|-------|-------|
| Dockerfile location | `frontend/Dockerfile` |
| Port | `3000` |
| Domain | `app.tudominio.com` |

```env
NEXT_PUBLIC_API_URL=https://api.tudominio.com
NEXT_PUBLIC_APP_NAME=Social AI Manager
```

---

## 7. Seed inicial (opcional, una sola vez)

Para crear usuario admin demo en la primera instalación:

1. Temporalmente en el backend: `RUN_SEED=true`
2. Redeploy
3. Verificar logs: `Seed complete: admin@socialmanager.local`
4. Volver a `RUN_SEED=false` y redeploy

Credenciales demo (cambiar en Fase 3):

- Email: `admin@example.com`
- Password: `Admin123!`

---

## 8. Volúmenes persistentes

| Ruta | Servicio | Uso |
|------|----------|-----|
| `/app/uploads` | Backend, Celery Worker | Assets generados (imágenes, videos) |

En Coolify → Backend → **Storages** → montar volumen persistente en `/app/uploads`.

---

## 9. SSL y dominios

Coolify gestiona Let's Encrypt automáticamente. Verificar:

- [ ] `https://app.tudominio.com` → frontend
- [ ] `https://api.tudominio.com/api/v1/health/ready` → `"status": "ready"`
- [ ] Redirect URI Meta actualizada a dominio producción

---

## 10. Backups

- **PostgreSQL**: activar backup automático en el recurso Coolify
- **Redis**: no crítico (cola efímera)
- **Uploads**: incluir volumen `/app/uploads` en backup del servidor

---

## 11. Escalado

| Servicio | Escalar | Notas |
|----------|---------|-------|
| Backend | ✅ Horizontal | Stateless; migraciones solo en una instancia* |
| Celery Worker | ✅ Horizontal | Más throughput de publicaciones |
| Celery Beat | ❌ | Exactamente 1 instancia |
| Frontend | ✅ Horizontal | Stateless |
| PostgreSQL | Vertical | Recurso gestionado por Coolify |
| Redis | Vertical | Recurso gestionado por Coolify |

\*Con `RUN_MIGRATIONS=true` en todas las réplicas, Alembic es idempotente — varias instancias pueden ejecutar `upgrade head` sin conflicto, aunque es más limpio migrar solo en deploy.

---

## 12. Troubleshooting Coolify

| Problema | Solución |
|----------|----------|
| Health check falla: `migrations: false` | Revisar logs del backend al arrancar; verificar `DATABASE_URL` |
| `database: false` | Usar Internal URL, no la pública |
| `postgres://` no conecta | Verificar que el backend esté en la misma red Coolify que PostgreSQL |
| Entrypoint error CRLF | El Dockerfile corrige CRLF con `sed`; asegurar `.gitattributes` con `eol=lf` |
| OAuth Meta falla | `META_REDIRECT_URI` debe ser HTTPS del dominio real |

---

## 13. Comandos manuales (terminal Coolify)

Solo si necesitas intervenir manualmente:

```bash
# Ver estado de migraciones
alembic current

# Aplicar migraciones manualmente
alembic upgrade head

# Seed manual
python -m app.scripts.seed
```
