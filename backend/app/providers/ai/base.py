from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class AIProviderType(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    REPLICATE = "replicate"
    STABILITY = "stability"
    NANO_BANANA = "nano_banana"
    LOCAL = "local"


class AICapability(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    EMBEDDING = "embedding"


class AIRequest(ABC):
    """Base request for AI operations."""

    prompt: str
    model: str | None
    metadata: dict[str, Any]


class AIResponse:
    def __init__(
        self,
        content: str | bytes,
        provider: AIProviderType,
        model: str,
        prompt: str,
        duration_ms: float,
        cost: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ):
        self.content = content
        self.provider = provider
        self.model = model
        self.prompt = prompt
        self.duration_ms = duration_ms
        self.cost = cost
        self.metadata = metadata or {}


class BaseAIProvider(ABC):
    """Interface that all AI providers must implement."""

    provider_type: AIProviderType
    capabilities: list[AICapability]

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    @abstractmethod
    def list_models(self, capability: AICapability) -> list[str]:
        ...
