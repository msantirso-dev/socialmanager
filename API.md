# API Reference — Social AI Manager

Base URL: `{BACKEND_URL}/api/v1`

Autenticación: **JWT Bearer** en header `Authorization: Bearer <access_token>`.

Endpoints públicos: `/health/*`, `/auth/login`, `/auth/register`, `/auth/refresh`.

---

## Auth

### `POST /auth/register`

Crea usuario + organización. El primer usuario es **admin** de la org.

**Body:**

```json
{
  "email": "user@example.com",
  "password": "minimo8chars",
  "full_name": "Nombre Apellido",
  "organization_name": "Mi Empresa"
}
```

**Response 200:**

```json
{
  "user": { "id": "...", "email": "...", "role": "admin", "organizations": [...] },
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### `POST /auth/login`

**Body:** `{ "email": "...", "password": "..." }`

**Response 200:** igual que register.

### `POST /auth/refresh`

**Body:** `{ "refresh_token": "..." }`

**Response 200:** nuevos `access_token` y `refresh_token`.

### `GET /auth/me`

Requiere JWT. Devuelve perfil + organizaciones del usuario.

### `POST /auth/logout`

Requiere JWT. Revoca el access token actual (blacklist Redis).

---

## Roles

| Rol | Nivel | Permisos |
|-----|-------|----------|
| `admin` | 4 | Acceso total |
| `editor` | 3 | Crear/editar contenido |
| `operator` | 2 | Publicar, operar |
| `readonly` | 1 | Solo lectura |

Usar dependency `require_role(UserRole.EDITOR)` en endpoints protegidos.

---

## Health

### `GET /health`

Estado básico del servicio.

**Response 200:**

```json
{
  "status": "ok",
  "service": "social-ai-manager-api"
}
```

### `GET /health/ready`

Readiness probe — verifica PostgreSQL y Redis.

**Response 200:**

```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true
  }
}
```

---

## Providers

### `GET /providers/ai`

Lista proveedores de IA registrados.

**Response 200:**

```json
{
  "providers": [
    {
      "type": "openai",
      "capabilities": ["text", "image", "embedding"],
      "models": {
        "text": ["gpt-4o", "gpt-4o-mini"],
        "image": ["dall-e-3"]
      }
    }
  ]
}
```

### `GET /providers/social`

Lista redes sociales disponibles.

**Response 200:**

```json
{
  "networks": [
    {
      "type": "instagram",
      "name": "Instagram",
      "available": true
    }
  ]
}
```

---

## Endpoints planificados por fase

| Fase | Prefijo | Descripción |
|------|---------|-------------|
| 3 ✅ | `/auth/*` | Login, registro, refresh, logout, me |
| 2 | `/companies/*` | CRUD empresas |
| 4 | `/social/instagram/*` | OAuth, publicar, métricas, comentarios |
| 5 | `/ai/generate/*` | Generación de contenido multi-IA |
| 5 | `/ai/images/*` | Generación de imágenes |
| 6 | `/posts/*` | Publicaciones, programación |
| 6 | `/calendar/*` | Calendario editorial |
| 8 | `/metrics/*` | Dashboard de métricas |
| 9 | `/comments/*` | Gestión de comentarios |

Documentación interactiva: `{BACKEND_URL}/docs` (Swagger UI)
