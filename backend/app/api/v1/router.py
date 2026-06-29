from fastapi import APIRouter

from app.api.v1.endpoints import auth, domain, health, providers

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(domain.router, tags=["Domain"])
api_router.include_router(providers.router, prefix="/providers", tags=["Providers"])
