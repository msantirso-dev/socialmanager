from app.providers.ai.anthropic_provider import AnthropicProvider
from app.providers.ai.google_provider import GoogleGeminiProvider
from app.providers.ai.openai_provider import OpenAIProvider
from app.providers.ai.registry import AIProviderRegistry
from app.providers.ai.stub_providers import NanoBananaProvider, ReplicateProvider, StabilityProvider


def init_ai_providers() -> None:
    """Register all AI providers at application startup."""
    AIProviderRegistry.register(OpenAIProvider())
    AIProviderRegistry.register(AnthropicProvider())
    AIProviderRegistry.register(GoogleGeminiProvider())
    AIProviderRegistry.register(ReplicateProvider())
    AIProviderRegistry.register(StabilityProvider())
    AIProviderRegistry.register(NanoBananaProvider())
