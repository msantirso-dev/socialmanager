## [1.0.0] - 2026-06-29

### Fases 4–10 — Plataforma completa

#### Fase 4 — Instagram
- Publicación imagen, carrusel y reel via Graph API
- OAuth connect/callback/disconnect/refresh
- Tokens cifrados en BD

#### Fase 5 — Generador IA
- `POST /ai/generate/content` — paquete completo (título, texto, hashtags, prompts, ideas)
- `POST /ai/generate/image` — DALL-E / proveedores registrados
- UI generador con preview

#### Fase 6 — Programador
- Celery Beat procesa posts programados cada minuto
- Reintentos automáticos (max 3)
- UI calendario con publicar ahora

#### Fase 7 — Dashboard
- Métricas en tiempo real: programadas, publicadas, engagement, créditos IA
- Próximas publicaciones

#### Fase 8 — Métricas
- Resumen por post: likes, comentarios, alcance
- UI métricas

#### Fase 9 — Comentarios
- Listado, respuesta manual y con IA
- Sync desde Instagram

#### Fase 10 — Deploy Coolify
- `docker-compose.prod.yml` — stack producción
- `frontend/Dockerfile.prod` — Next.js standalone
- Health checks, volúmenes uploads, RUN_MIGRATIONS

#### API endpoints añadidos
- `/companies`, `/social/*`, `/posts`, `/ai/*`, `/dashboard`, `/metrics`, `/comments`

---
