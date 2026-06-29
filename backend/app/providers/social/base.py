from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any


class SocialNetworkType(StrEnum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    THREADS = "threads"
    PINTEREST = "pinterest"
    GOOGLE_BUSINESS = "google_business"
    WORDPRESS = "wordpress"


class PostType(StrEnum):
    IMAGE = "image"
    CAROUSEL = "carousel"
    REEL = "reel"
    VIDEO = "video"
    STORY = "story"
    TEXT = "text"


class SocialAccountInfo:
    def __init__(
        self,
        account_id: str,
        username: str,
        display_name: str,
        profile_picture_url: str | None = None,
        followers_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.account_id = account_id
        self.username = username
        self.display_name = display_name
        self.profile_picture_url = profile_picture_url
        self.followers_count = followers_count
        self.metadata = metadata or {}


class PublishResult:
    def __init__(
        self,
        success: bool,
        external_id: str | None = None,
        permalink: str | None = None,
        error: str | None = None,
        raw_response: dict[str, Any] | None = None,
    ):
        self.success = success
        self.external_id = external_id
        self.permalink = permalink
        self.error = error
        self.raw_response = raw_response or {}


class BaseSocialProvider(ABC):
    """Interface that all social network modules must implement."""

    network_type: SocialNetworkType

    @abstractmethod
    def get_oauth_url(self, state: str) -> str:
        """Return OAuth authorization URL."""
        ...

    @abstractmethod
    async def handle_oauth_callback(self, code: str) -> dict[str, Any]:
        """Exchange code for tokens. Returns access_token, refresh info, account data."""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_account_info(self, access_token: str) -> SocialAccountInfo:
        ...

    @abstractmethod
    async def publish_image(
        self,
        access_token: str,
        account_id: str,
        image_url: str,
        caption: str,
        scheduled_at: datetime | None = None,
    ) -> PublishResult:
        ...

    @abstractmethod
    async def publish_carousel(
        self,
        access_token: str,
        account_id: str,
        media_urls: list[str],
        caption: str,
        scheduled_at: datetime | None = None,
    ) -> PublishResult:
        ...

    @abstractmethod
    async def publish_reel(
        self,
        access_token: str,
        account_id: str,
        video_url: str,
        caption: str,
        cover_url: str | None = None,
        scheduled_at: datetime | None = None,
    ) -> PublishResult:
        ...

    @abstractmethod
    async def get_posts(
        self,
        access_token: str,
        account_id: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_metrics(
        self,
        access_token: str,
        post_id: str,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_comments(
        self,
        access_token: str,
        post_id: str,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def reply_comment(
        self,
        access_token: str,
        comment_id: str,
        message: str,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def disconnect(self, access_token: str) -> bool:
        ...
