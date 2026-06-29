import json
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import LogCategory, log_event
from app.models.ai import AIHistory
from app.providers.ai.base import AIProviderType
from app.providers.ai.registry import AIProviderRegistry
from app.schemas.domain import AIContentResponse, GenerateContentRequest, GenerateImageRequest
from app.services.company_service import get_company
from app.models.user import User


GENERATION_SYSTEM = """Eres un experto en marketing digital y redes sociales.
Genera contenido en JSON válido con estas claves exactas:
title, text, description, cta, hashtags (array), seo (object con title y description),
image_prompt, video_prompt, reel_ideas (array), story_ideas (array), carousel_ideas (array),
variants (array de textos alternativos), tones (array de tonos sugeridos).
Responde SOLO JSON, sin markdown."""


async def generate_content(db: AsyncSession, user: User, data: GenerateContentRequest) -> AIContentResponse:
    company = await get_company(db, user, data.company_id)
    provider_name = data.text_provider or "anthropic"
    provider_type = AIProviderType(provider_name)
    provider = AIProviderRegistry.get(provider_type)
    model = data.text_model

    prompt = f"""Concepto: {data.concept}
Marca: {company.name}
Tono: {company.tone or 'professional'}
Idioma: {company.language}
Público: {company.target_audience or 'general'}
Hashtags propios: {', '.join(company.custom_hashtags or [])}
Palabras prohibidas: {', '.join(company.forbidden_words or [])}"""

    start = time.perf_counter()
    response = await provider.generate_text(prompt, model=model, system_prompt=GENERATION_SYSTEM, temperature=0.8)
    duration_ms = (time.perf_counter() - start) * 1000

    try:
        content = json.loads(response.content if isinstance(response.content, str) else "{}")
    except json.JSONDecodeError:
        content = {"title": data.concept[:80], "text": str(response.content), "hashtags": [], "description": "", "cta": "", "seo": {}, "image_prompt": "", "video_prompt": "", "reel_ideas": [], "story_ideas": [], "carousel_ideas": [], "variants": [], "tones": []}

    history = AIHistory(
        company_id=company.id,
        provider=provider_name,
        model=model or "default",
        capability="text",
        prompt=prompt,
        response=str(response.content)[:10000],
        cost=float(response.cost or 0),
        duration_ms=duration_ms,
    )
    db.add(history)
    await db.flush()
    await log_event(LogCategory.AI, "generate_content", user_id=str(user.id), company_id=str(company.id), cost=response.cost, duration_ms=duration_ms)

    return AIContentResponse(
        title=content.get("title", ""),
        text=content.get("text", ""),
        description=content.get("description", ""),
        cta=content.get("cta", ""),
        hashtags=content.get("hashtags", []),
        seo=content.get("seo", {}),
        image_prompt=content.get("image_prompt", ""),
        video_prompt=content.get("video_prompt", ""),
        reel_ideas=content.get("reel_ideas", []),
        story_ideas=content.get("story_ideas", []),
        carousel_ideas=content.get("carousel_ideas", []),
        variants=content.get("variants", []),
        tones=content.get("tones", []),
        provider=provider_name,
        model=model or "default",
        cost=float(response.cost or 0),
        duration_ms=duration_ms,
    )


async def generate_image(db: AsyncSession, user: User, data: GenerateImageRequest) -> dict:
    company = await get_company(db, user, data.company_id)
    provider_type = AIProviderType(data.provider)
    provider = AIProviderRegistry.get(provider_type)
    start = time.perf_counter()
    response = await provider.generate_image(data.prompt, model=data.model, width=data.width, height=data.height)
    duration_ms = (time.perf_counter() - start) * 1000

    from app.models.asset import Asset
    from app.models.enums import AssetType

    url = response.content if isinstance(response.content, str) else ""
    asset = Asset(
        company_id=company.id,
        type=AssetType.IMAGE,
        url=url,
        ai_provider=data.provider,
        ai_model=data.model or "default",
        ai_prompt=data.prompt,
        ai_cost=float(response.cost or 0),
        ai_duration_ms=duration_ms,
        width=data.width,
        height=data.height,
    )
    db.add(asset)
    db.add(AIHistory(
        company_id=company.id, provider=data.provider, model=data.model or "default",
        capability="image", prompt=data.prompt, response=url, cost=float(response.cost or 0), duration_ms=duration_ms,
    ))
    await db.flush()
    return {"url": url, "asset_id": str(asset.id), "prompt": data.prompt, "provider": data.provider, "duration_ms": duration_ms, "cost": float(response.cost or 0)}
