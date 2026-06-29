from fastapi import APIRouter

from app.providers.ai.registry import AIProviderRegistry
from app.providers.social.registry import SocialProviderRegistry

router = APIRouter()


@router.get("/ai")
async def list_ai_providers():
    return {"providers": AIProviderRegistry.list_providers()}


@router.get("/social")
async def list_social_networks():
    return {"networks": SocialProviderRegistry.list_networks()}
