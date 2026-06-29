# Guía de instalación — Social AI Manager

Documento paso a paso para instalar y configurar la plataforma completa.

---

## Tabla de contenidos

1. [Requisitos](#1-requisitos)
2. [Crear App en Meta Developers](#2-crear-app-en-meta-developers)
3. [Crear API Keys de IA](#3-crear-api-keys-de-ia)
4. [Variables de entorno](#4-variables-de-entorno)
5. [Instalación del proyecto](#5-instalación-del-proyecto)
6. [Verificación](#6-verificación)
7. [Solución de problemas](#7-solución-de-problemas)

---

## 1. Requisitos

### Software obligatorio

| Herramienta | Versión mínima | Verificar |
|-------------|----------------|-----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2.20+ | `docker compose version` |
| Git | 2.40+ | `git --version` |

### Software opcional (desarrollo local sin Docker)

| Herramienta | Versión mínima | Verificar |
|-------------|----------------|-----------|
| Node.js | 20 LTS | `node --version` |
| Python | 3.12 | `python --version` |
| PostgreSQL | 16 | `psql --version` |
| Redis | 7 | `redis-cli --version` |

### Infraestructura de producción

| Recurso | Descripción |
|---------|-------------|
| Servidor VPS/Cloud | Mínimo 2 vCPU, 4 GB RAM |
| Dominio | Ej: `app.tudominio.com` |
| SSL | Certificado HTTPS (Coolify lo gestiona con Let's Encrypt) |
| Coolify | Instancia configurada en el servidor |

---

## 2. Crear App en Meta Developers

> **Importante:** Usa únicamente procedimientos y endpoints oficiales de Meta. La versión de API configurada por defecto es `v21.0`. Si Meta publica una versión nueva, actualiza `META_GRAPH_API_VERSION` en `.env`.

### 2.1 Crear cuenta en Meta Developers

1. Ve a [developers.facebook.com](https://developers.facebook.com/)
2. Inicia sesión con tu cuenta de Facebook
3. Acepta los términos de desarrollador si es la primera vez

### 2.2 Crear una nueva aplicación

1. Clic en **Mis apps** → **Crear app**
2. Selecciona tipo de caso de uso: **Otro** (o **Empresa** si gestionas cuentas de clientes)
3. Tipo de app: **Empresa**
4. Nombre: `Social AI Manager` (o el que prefieras)
5. Email de contacto: tu email
6. Clic en **Crear app**

### 2.3 Agregar producto Instagram Graph API

1. En el panel de la app, ve a **Agregar productos**
2. Busca **Instagram Graph API** (o **Instagram** dentro de la suite de Meta Business)
3. Clic en **Configurar**

> Si el producto aparece como "Instagram" dentro de "Facebook Login for Business", agrégalo también.

### 2.4 Vincular Página de Facebook

Instagram Business/Creator requiere una Página de Facebook vinculada:

1. Crea una Página de Facebook en [facebook.com/pages/create](https://www.facebook.com/pages/create) si no tienes una
2. En Meta Developers → tu app → **Roles** → agrega tu cuenta como administrador
3. En Instagram → Configuración → **Cuenta profesional** → vincula la Página de Facebook

### 2.5 Vincular cuenta profesional de Instagram

1. Abre Instagram → **Configuración y privacidad** → **Tipo de cuenta y herramientas**
2. Cambia a **Cuenta profesional** (Business o Creator)
3. Vincula la Página de Facebook creada anteriormente

### 2.6 Configurar OAuth — URL de redirección

1. En Meta Developers → tu app → **Facebook Login** → **Configuración**
2. En **URI de redireccionamiento de OAuth válidos**, agrega:
   - Desarrollo: `http://localhost:8000/api/v1/social/instagram/callback`
   - Producción: `https://api.tudominio.com/api/v1/social/instagram/callback`
3. Guarda cambios

### 2.7 Configurar permisos

Solicita estos permisos (App Review requerido para producción):

| Permiso | Uso |
|---------|-----|
| `instagram_basic` | Perfil y medios básicos |
| `instagram_content_publish` | Publicar contenido |
| `instagram_manage_comments` | Gestionar comentarios |
| `instagram_manage_insights` | Métricas e insights |
| `pages_show_list` | Listar páginas del usuario |
| `pages_read_engagement` | Engagement de la página |

### 2.8 Obtener credenciales

1. **App ID**: Panel → **Configuración** → **Básica** → ID de la app
2. **App Secret**: Mismo panel → **Secreto de la app** → Mostrar

Copia ambos valores a `.env`:

```env
META_APP_ID=tu_app_id
META_APP_SECRET=tu_app_secret
META_REDIRECT_URI=http://localhost:8000/api/v1/social/instagram/callback
META_GRAPH_API_VERSION=v21.0
```

### 2.9 Tokens: temporal vs larga duración

| Tipo | Duración | Uso |
|------|----------|-----|
| **Token de usuario temporal** | ~1 hora | Resultado directo del OAuth |
| **Token de larga duración** | ~60 días | Se obtiene intercambiando el temporal |

**Intercambio (endpoint oficial):**

```http
GET https://graph.facebook.com/v21.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={APP_ID}
  &client_secret={APP_SECRET}
  &fb_exchange_token={SHORT_LIVED_TOKEN}
```

La plataforma hace este intercambio automáticamente en el callback OAuth (Fase 4).

### 2.10 Renovar token

Los tokens de larga duración expiran. Para renovar:

```http
GET https://graph.facebook.com/v21.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={APP_ID}
  &client_secret={APP_SECRET}
  &fb_exchange_token={CURRENT_LONG_LIVED_TOKEN}
```

El scheduler de la plataforma validará y renovará tokens automáticamente (Fase 6).

### 2.11 Probar con Graph API Explorer

1. Ve a [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer/)
2. Selecciona tu app
3. Genera un token con los permisos necesarios
4. Prueba: `GET /me/accounts` → debe listar tus páginas
5. Obtén el ID de Instagram: `GET /{page-id}?fields=instagram_business_account`
6. Prueba medios: `GET /{ig-user-id}/media`

### 2.12 Verificar permisos antes de publicar

Antes de habilitar publicación en producción:

- [ ] App en modo **Live** (no Development)
- [ ] Permisos aprobados en **App Review**
- [ ] Cuenta Instagram es **Business/Creator**
- [ ] Página de Facebook vinculada correctamente
- [ ] Token de larga duración almacenado (cifrado con AES en la BD)

---

## 3. Crear API Keys de IA

### 3.1 OpenAI

1. Registrarse: [platform.openai.com/signup](https://platform.openai.com/signup)
2. Ir a **API keys** → **Create new secret key**
3. Permisos: acceso a Chat Completions e Images
4. Copiar la clave (solo se muestra una vez)
5. Probar:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-..."
```

Almacenar en `.env`: `OPENAI_API_KEY=sk-...`

### 3.2 Anthropic (Claude)

1. Registrarse: [console.anthropic.com](https://console.anthropic.com/)
2. **Settings** → **API Keys** → **Create Key**
3. Copiar clave
4. Probar:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: sk-ant-..." \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-haiku-20241022","max_tokens":100,"messages":[{"role":"user","content":"Hola"}]}'
```

Almacenar: `ANTHROPIC_API_KEY=sk-ant-...`

### 3.3 Google AI (Gemini)

1. Registrarse: [aistudio.google.com](https://aistudio.google.com/)
2. **Get API key** → **Create API key**
3. Seleccionar proyecto de Google Cloud
4. Probar en AI Studio o:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

Almacenar: `GOOGLE_API_KEY=...`

### 3.4 Replicate

1. Registrarse: [replicate.com](https://replicate.com/)
2. **Account** → **API tokens** → **Create token**
3. Probar:

```bash
curl -s -H "Authorization: Bearer r8_..." https://api.replicate.com/v1/models
```

Almacenar: `REPLICATE_API_TOKEN=r8_...`

### 3.5 Stability AI

1. Registrarse: [platform.stability.ai](https://platform.stability.ai/)
2. **Account** → **API Keys** → **Create API Key**
3. Almacenar: `STABILITY_API_KEY=sk-...`

### 3.6 Nano Banana

> Si el proveedor dispone de API pública, seguir su documentación oficial. Actualmente registrado como stub en la arquitectura; implementación completa en Fase 5.

Almacenar: `NANO_BANANA_API_KEY=...`

### Almacenamiento seguro de claves

- **Nunca** commitear `.env` al repositorio
- Usar `.env.example` como plantilla (sin valores reales)
- En producción: variables de entorno de Coolify (secretos)
- Rotar claves periódicamente
- La plataforma cifra tokens OAuth con AES-256 (`ENCRYPTION_KEY`)

---

## 4. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores. Referencia completa en `.env.example`.

Generar `ENCRYPTION_KEY` segura:

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Generar `JWT_SECRET` y `SECRET_KEY`:

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 5. Instalación del proyecto

### 5.1 Clonar repositorio

```bash
git clone <repo-url> social-ai-manager
cd social-ai-manager
cp .env.example .env
# Editar .env con tus credenciales
```

### 5.2 Levantar con Docker Compose

```bash
docker compose up -d
```

Servicios levantados:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `postgres` | 5432 | Base de datos |
| `redis` | 6379 | Cache y broker Celery |
| `backend` | 8000 | API FastAPI |
| `celery-worker` | — | Procesador de tareas |
| `celery-beat` | — | Scheduler (cada minuto) |
| `frontend` | 3000 | Next.js |

### 5.3 Migraciones

Las migraciones se aplican **automáticamente** al arrancar el backend (`RUN_MIGRATIONS=true`).

Manualmente si hace falta:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

### 5.4 Seed (primera instalación)

```bash
# Opción A: variable de entorno
RUN_SEED=true docker compose up -d backend

# Opción B: manual
docker compose exec backend python -m app.scripts.seed
```

Credenciales demo: `admin@example.com` / `Admin123!`

### 5.5 Desarrollo local sin Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Celery (terminal separada):**

```bash
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### 5.6 Compilar frontend para producción

```bash
cd frontend
npm run build
npm start
```

---

## 6. Verificación

### Health checks

```bash
# API básica
curl http://localhost:8000/api/v1/health

# Readiness (DB + Redis)
curl http://localhost:8000/api/v1/health/ready

# Proveedores registrados
curl http://localhost:8000/api/v1/providers/ai
curl http://localhost:8000/api/v1/providers/social
```

### Frontend

Abrir [http://localhost:3000](http://localhost:3000) — debe mostrar el panel de estado con servicios conectados.

### Swagger

Abrir [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 7. Solución de problemas

| Problema | Solución |
|----------|----------|
| Backend no conecta a PostgreSQL | Verificar que `postgres` esté healthy: `docker compose ps` |
| Redis connection refused | Esperar healthcheck: `docker compose logs redis` |
| Frontend muestra "Backend no disponible" | Verificar `NEXT_PUBLIC_API_URL` apunta al backend |
| Puerto ya en uso (5432, 8000, 3000) | Cambiar mapeo en `docker-compose.yml` o detener el servicio conflictivo |
| Meta OAuth falla | Verificar redirect URI exacta en Meta Developers |
| Celery no ejecuta tareas | Verificar worker: `docker compose logs celery-worker` |

---

Ver también: [DEPLOY.md](./DEPLOY.md) para producción en Coolify.
