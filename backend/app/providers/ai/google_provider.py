import time
from typing import Any

from app.core.config import settings
from app.providers.ai.base import AICapability, AIProviderType, AIResponse, BaseAIProvider


class GoogleGeminiProvider(BaseAIProvider):
    provider_type = AIProviderType.GOOGLE
    capabilities = [AICapability.TEXT, AICapability.IMAGE]

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or settings.google_api_key

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
            raise ValueError("Google API key not configured")

        import google.generativeai as genai

        genai.configure(api_key=self._api_key)
        model_name = model or "gemini-1.5-flash"
        gemini_model = genai.GenerativeModel(model_name, system_instruction=system_prompt)

        start = time.perf_counter()
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": temperature},
        )
        duration_ms = (time.perf_counter() - start) * 1000

        return AIResponse(
            content=response.text or "",
            provider=self.provider_type,
            model=model_name,
            prompt=prompt,
            duration_ms=duration_ms,
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
        raise NotImplementedError("Gemini image generation will be implemented in Phase 5")

    async def health_check(self) -> bool:
        return bool(self._api_key)

    def list_models(self, capability: AICapability) -> list[str]:
        if capability == AICapability.TEXT:
            return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
        return []
