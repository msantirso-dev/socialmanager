from app.providers.ai.base import AIProviderType, BaseAIProvider


class AIProviderRegistry:
    """Registry for pluggable AI providers. UI can switch provider at runtime."""

    _providers: dict[AIProviderType, BaseAIProvider] = {}

    @classmethod
    def register(cls, provider: BaseAIProvider) -> None:
        cls._providers[provider.provider_type] = provider

    @classmethod
    def get(cls, provider_type: AIProviderType) -> BaseAIProvider:
        if provider_type not in cls._providers:
            raise KeyError(f"AI provider '{provider_type}' is not registered")
        return cls._providers[provider_type]

    @classmethod
    def list_providers(cls) -> list[dict]:
        return [
            {
                "type": p.provider_type.value,
                "capabilities": [c.value for c in p.capabilities],
                "models": {
                    cap.value: p.list_models(cap)
                    for cap in p.capabilities
                },
            }
            for p in cls._providers.values()
        ]

    @classmethod
    def is_registered(cls, provider_type: AIProviderType) -> bool:
        return provider_type in cls._providers
