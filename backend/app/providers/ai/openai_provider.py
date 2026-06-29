import time
from typing import Any

from app.core.config import settings
from app.providers.ai.base import AICapability, AIProviderType, AIResponse, BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    provider_type = AIProviderType.OPENAI
    capabilities = [AICapability.TEXT, AICapability.IMAGE, AICapability.EMBEDDING]

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or settings.openai_api_key

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AIResponse:
        if not self._api_key:
            raise ValueError("OpenAI API key not configured")

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key)
        model = model or "gpt-4o-mini"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.perf_counter()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        duration_ms = (time.perf_counter() - start) * 1000

        content = response.choices[0].message.content or ""
        return AIResponse(
            content=content,
            provider=self.provider_type,
            model=model,
            prompt=prompt,
            duration_ms=duration_ms,
            metadata={"usage": response.usage.model_dump() if response.usage else {}},
        )

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str | None = None,
        width: int = 1024,
        height: int = 1024,
        aspect_ratio: str | None = None,
        **kwargs: Any,
    ) -> AIResponse:
        if not self._api_key:
            raise ValueError("OpenAI API key not configured")

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key)
        model = model or "dall-e-3"
        size = f"{width}x{height}" if width and height else "1024x1024"

        start = time.perf_counter()
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,  # type: ignore[arg-type]
            n=1,
        )
        duration_ms = (time.perf_counter() - start) * 1000

        url = response.data[0].url or ""
        return AIResponse(
            content=url,
            provider=self.provider_type,
            model=model,
            prompt=prompt,
            duration_ms=duration_ms,
            metadata={"revised_prompt": response.data[0].revised_prompt},
        )

    async def health_check(self) -> bool:
        return bool(self._api_key)

    def list_models(self, capability: AICapability) -> list[str]:
        if capability == AICapability.TEXT:
            return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        if capability == AICapability.IMAGE:
            return ["dall-e-3", "dall-e-2"]
        return []
