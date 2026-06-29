import time
from typing import Any

from app.core.config import settings
from app.providers.ai.base import AICapability, AIProviderType, AIResponse, BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    provider_type = AIProviderType.ANTHROPIC
    capabilities = [AICapability.TEXT]

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or settings.anthropic_api_key

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
            raise ValueError("Anthropic API key not configured")

        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self._api_key)
        model = model or "claude-3-5-sonnet-20241022"

        start = time.perf_counter()
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        duration_ms = (time.perf_counter() - start) * 1000

        content = response.content[0].text if response.content else ""
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
        raise NotImplementedError("Anthropic does not support image generation via this interface")

    async def health_check(self) -> bool:
        return bool(self._api_key)

    def list_models(self, capability: AICapability) -> list[str]:
        if capability == AICapability.TEXT:
            return ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
        return []
