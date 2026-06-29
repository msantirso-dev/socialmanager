# Proveedores de IA — Social AI Manager

Arquitectura desacoplada con interfaz común (`BaseAIProvider`). Cambio de proveedor configurable desde la UI.

---

## Interfaz común

Todos los proveedores implementan:

```python
class BaseAIProvider(ABC):
    provider_type: AIProviderType
    capabilities: list[AICapability]

    async def generate_text(prompt, *, model, system_prompt, ...) -> AIResponse
    async def generate_image(prompt, *, model, width, height, ...) -> AIResponse
    async def health_check() -> bool
    def list_models(capability: AICapability) -> list[str]
```

Registro en runtime via `AIProviderRegistry`.

---

## Proveedores

| Proveedor | ID | Texto | Imagen | Video | Estado |
|-----------|-----|-------|--------|-------|--------|
| OpenAI | `openai` | ✅ | ✅ DALL-E | — | Implementado |
| Anthropic | `anthropic` | ✅ Claude | — | — | Implementado |
| Google Gemini | `google` | ✅ | 🔜 | — | Texto implementado |
| Replicate | `replicate` | — | ✅ | ✅ | Stub (Fase 5) |
| Stability AI | `stability` | — | ✅ | — | Stub (Fase 5) |
| Nano Banana | `nano_banana` | ✅ | ✅ | — | Stub (Fase 5) |
| Local | `local` | — | — | — | Futuro |

---

## Multi-IA por publicación

Cada publicación puede usar proveedores distintos:

```json
{
  "ai_config": {
    "text": { "provider": "anthropic", "model": "claude-3-5-sonnet-20241022" },
    "image": { "provider": "openai", "model": "dall-e-3" },
    "hashtags": { "provider": "google", "model": "gemini-1.5-flash" },
    "ideas": { "provider": "openai", "model": "gpt-4o-mini" }
  }
}
```

Configurable por empresa en tabla `ai_configs` (Fase 2).

---

## Generador de contenido (Fase 5)

Input: concepto de negocio

Output automático:

- Título
- Texto / descripción
- CTA
- Hashtags
- SEO metadata
- Prompt para imagen
- Prompt para video
- Ideas para Reel, Story, Carrusel
- Variantes de tono

---

## Generador de imágenes (Fase 5)

Parámetros configurables:

| Parámetro | Opciones |
|-----------|----------|
| Proveedor | openai, replicate, stability... |
| Cantidad | 1-4 |
| Formato | png, jpg, webp |
| Resolución | 512-2048 |
| Relación de aspecto | 1:1, 4:5, 16:9, 9:16 |
| Modelo | Según proveedor |

Output guardado en tabla `assets` con metadatos completos (prompt, costo, tiempo, proveedor).

---

## Costos y logging

Cada llamada IA registra en `ai_history`:

- Proveedor y modelo
- Prompt y respuesta
- Tokens utilizados
- Costo estimado (USD)
- Duración (ms)

Dashboard de créditos en Fase 7.

---

## Configuración

Variables en `.env`:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
REPLICATE_API_TOKEN=r8_...
STABILITY_API_KEY=sk-...
NANO_BANANA_API_KEY=...
```

Ver [INSTALL.md](./INSTALL.md) sección 3 para obtener cada clave.

---

## API endpoints (Fase 5)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/providers/ai` | Listar proveedores |
| POST | `/ai/generate/content` | Generar paquete completo |
| POST | `/ai/generate/text` | Solo texto |
| POST | `/ai/generate/image` | Generar imagen(es) |
| GET | `/ai/history` | Historial de generaciones |
