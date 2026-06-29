# Social AI Manager

Plataforma SaaS de generación automática de contenido con IA y publicación en redes sociales.

## Stack

| Capa | Tecnología |
|------|------------|
| Frontend | Next.js 15, React 19, Tailwind CSS, Shadcn UI |
| Backend | FastAPI (Python 3.12) |
| Base de datos | PostgreSQL 16 |
| Cache / Cola | Redis 7 |
| Scheduler | Celery + Celery Beat |
| Contenedores | Docker + Docker Compose |
| Deploy | Coolify |

## Inicio rápido

```bash
# 1. Clonar y configurar
git clone <repo-url> social-ai-manager
cd social-ai-manager
cp .env.example .env

# 2. Levantar todo el stack
docker compose up -d

# 3. Acceder
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

## Estructura del proyecto

```
social-manager/
├── frontend/                 # Next.js app
│   └── src/
│       ├── app/              # App Router pages
│       ├── components/       # UI + layout
│       └── lib/              # Utils, API client
├── backend/                  # FastAPI app
│   └── app/
│       ├── api/v1/           # REST endpoints
│       ├── core/             # Config, DB, security, logging
│       ├── providers/
│       │   ├── ai/           # Proveedores IA (interfaz desacoplada)
│       │   └── social/       # Redes sociales (módulos independientes)
│       ├── tasks/            # Celery tasks (scheduler)
│       ├── models/           # SQLAlchemy (Fase 2)
│       ├── schemas/          # Pydantic (Fase 2+)
│       └── services/         # Lógica de negocio
├── docker-compose.yml
├── .env.example
└── docs/                     # Documentación detallada
```

## Fases de desarrollo

| Fase | Módulo | Estado |
|------|--------|--------|
| 1 | Arquitectura | ✅ Completada |
| 2 | Base de datos | ✅ Completada |
| 3 | Login / Auth JWT | ✅ Completada |
| 4 | Conexión Instagram | ✅ Completada |
| 5 | Generación IA | ✅ Completada |
| 6 | Programador | ✅ Completada |
| 7 | Dashboard | ✅ Completada |
| 8 | Métricas | ✅ Completada |
| 9 | Comentarios | ✅ Completada |
| 10 | Deploy Coolify | ✅ Completada |

## Documentación

- [INSTALL.md](./INSTALL.md) — Instalación paso a paso
- [API.md](./API.md) — Referencia de endpoints
- [DATABASE.md](./DATABASE.md) — Esquema de base de datos
- [DEPLOY.md](./DEPLOY.md) — Despliegue en Coolify
- [META_SETUP.md](./META_SETUP.md) — Configuración Meta/Instagram
- [AI_PROVIDERS.md](./AI_PROVIDERS.md) — Proveedores de IA
- [CHANGELOG.md](./CHANGELOG.md) — Historial de cambios

## Licencia

Proprietary — All rights reserved.
