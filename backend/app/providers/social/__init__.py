from app.providers.social.instagram import InstagramProvider
from app.providers.social.registry import SocialProviderRegistry


def init_social_providers() -> None:
    SocialProviderRegistry.register(InstagramProvider())
