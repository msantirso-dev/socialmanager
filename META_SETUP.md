# Configuración Meta / Instagram Graph API

Guía específica para la integración con Instagram. Ver también [INSTALL.md](./INSTALL.md) sección 2.

---

## Versión de API

La plataforma usa la versión configurada en `META_GRAPH_API_VERSION` (default: `v21.0`).

Base URL: `https://graph.facebook.com/{version}`

> Consulta [Meta Graph API Changelog](https://developers.facebook.com/docs/graph-api/changelog) para versiones vigentes.

---

## Requisitos de cuenta

1. **Cuenta Instagram Business o Creator** — cuentas personales no soportan la Graph API de publicación
2. **Página de Facebook vinculada** — obligatorio para Instagram Business
3. **App Meta en modo Live** — con permisos aprobados en App Review (producción)

---

## Flujo OAuth implementado

```
Usuario → /api/v1/social/instagram/connect
       → Redirect a Facebook OAuth
       → Usuario autoriza permisos
       → Callback /api/v1/social/instagram/callback?code=...
       → Intercambio code → token corto
       → Intercambio token corto → token largo (60 días)
       → Obtener Page + Instagram Business Account
       → Cifrar y guardar token en BD
       → Redirect a frontend con éxito
```

Implementación completa en **Fase 4**.

---

## Permisos requeridos

| Permiso | Endpoint relacionado |
|---------|---------------------|
| `instagram_basic` | Perfil, medios |
| `instagram_content_publish` | POST `/{ig-user-id}/media` |
| `instagram_manage_comments` | GET/POST comentarios |
| `instagram_manage_insights` | GET insights |
| `pages_show_list` | GET `/me/accounts` |
| `pages_read_engagement` | Métricas de página |

---

## Publicación de contenido

### Imagen simple

```
1. POST /{ig-user-id}/media
   { image_url, caption, access_token }

2. POST /{ig-user-id}/media_publish
   { creation_id, access_token }
```

### Carrusel

```
1. POST /{ig-user-id}/media (por cada imagen, is_carousel_item=true)
2. POST /{ig-user-id}/media (media_type=CAROUSEL, children=ids)
3. POST /{ig-user-id}/media_publish
```

### Reel

```
1. POST /{ig-user-id}/media
   { media_type=REELS, video_url, caption, cover_url }
2. POST /{ig-user-id}/media_publish
```

Implementación en **Fase 4**.

---

## Métricas (Insights)

```http
GET /{ig-media-id}/insights
  ?metric=impressions,reach,engagement,saved,shares
  &access_token={token}
```

Para cuenta:

```http
GET /{ig-user-id}/insights
  ?metric=impressions,reach,follower_count
  &period=day
```

---

## Comentarios

```http
# Listar
GET /{ig-media-id}/comments?fields=id,text,timestamp,username

# Responder
POST /{comment-id}/replies
  { message: "Gracias por tu comentario!" }

# Ocultar
POST /{comment-id}
  { hide: true }
```

---

## Renovación de tokens

Programada automáticamente por el scheduler (Fase 6). Manualmente:

```http
GET /oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={APP_ID}
  &client_secret={APP_SECRET}
  &fb_exchange_token={CURRENT_TOKEN}
```

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `(#190) Invalid OAuth 2.0 Access Token` | Token expirado | Renovar token |
| `(#10) Application does not have permission` | Permiso no aprobado | App Review |
| `(#100) Invalid parameter` | URL de imagen no accesible públicamente | Usar URL pública HTTPS |
| `Instagram account is not a Business account` | Cuenta personal | Convertir a Business/Creator |

---

## Seguridad

- Tokens almacenados cifrados con AES-256 (`ENCRYPTION_KEY`)
- Nunca loguear tokens en texto plano
- Validar token antes de cada publicación programada
- Rate limiting en endpoints OAuth
