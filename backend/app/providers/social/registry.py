from app.providers.social.base import BaseSocialProvider, SocialNetworkType


class SocialProviderRegistry:
    _providers: dict[SocialNetworkType, BaseSocialProvider] = {}

    @classmethod
    def register(cls, provider: BaseSocialProvider) -> None:
        cls._providers[provider.network_type] = provider

    @classmethod
    def get(cls, network_type: SocialNetworkType) -> BaseSocialProvider:
        if network_type not in cls._providers:
            raise KeyError(f"Social network '{network_type}' is not registered")
        return cls._providers[network_type]

    @classmethod
    def list_networks(cls) -> list[dict]:
        return [
            {
                "type": p.network_type.value,
                "name": p.network_type.value.replace("_", " ").title(),
                "available": p.network_type == SocialNetworkType.INSTAGRAM,
            }
            for p in cls._providers.values()
        ]
