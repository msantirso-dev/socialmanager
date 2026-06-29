"""Stub providers — full implementation in Phase 5."""

import time
from typing import Any

from app.core.config import settings
from app.providers.ai.base import AICapability, AIProviderType, AIResponse, BaseAIProvider


class _StubProvider(BaseAIProvider):
    def __init__(self, provider_type: AIProviderType, capabilities: list[AICapability], api_key: str):
        self.provider_type = provider_type
        self.capabilities = capabilities
        self._api_key = api_key

    async def generate_text(self, prompt: str, **kwargs: Any) -> AIResponse:
        if not self._api_key:
            raise ValueError(f"{self.provider_type.value} API key not configured")
        return AIResponse(
            content=f"[Stub {self.provider_type.value}] Response for: {prompt[:100]}",
            provider=self.provider_type,
            model=kwargs.get("model") or "default",
            prompt=prompt,
            duration_ms=0,
        )

    async def generate_image(self, prompt: str, **kwargs: Any) -> AIResponse:
        if not self._api_key:
            raise ValueError(f"{self.provider_type.value} API key not configured")
        return AIResponse(
            content=b"",
            provider=self.provider_type,
            model=kwargs.get("model") or "default",
            prompt=prompt,
            duration_ms=0,
        )

    async def health_check(self) -> bool:
        return bool(self._api_key)

    def list_models(self, capability: AICapability) -> list[str]:
        return ["default"]


class ReplicateProvider(_StubProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(AIProviderType.REPLICATE, [AICapability.IMAGE, AICapability.VIDEO], api_key or settings.replicate_api_token)


class StabilityProvider(_StubProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(AIProviderType.STABILITY, [AICapability.IMAGE], api_key or settings.stability_api_key)


class NanoBananaProvider(_StubProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(AIProviderType.NANO_BANANA, [AICapability.TEXT, AICapability.IMAGE], api_key or settings.nano_banana_api_key)
