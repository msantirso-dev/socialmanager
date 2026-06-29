from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.providers.social.base import (
    BaseSocialProvider,
    PublishResult,
    SocialAccountInfo,
    SocialNetworkType,
)


class InstagramProvider(BaseSocialProvider):
    """
    Instagram Graph API provider.
    Full implementation in Phase 4; OAuth and token exchange scaffolded here.
    """

    network_type = SocialNetworkType.INSTAGRAM

    SCOPES = [
        "instagram_basic",
        "instagram_content_publish",
        "instagram_manage_comments",
        "instagram_manage_insights",
        "pages_show_list",
        "pages_read_engagement",
    ]

    @property
    def _graph_url(self) -> str:
        return settings.meta_graph_base_url

    def get_oauth_url(self, state: str) -> str:
        params = {
            "client_id": settings.meta_app_id,
            "redirect_uri": settings.meta_redirect_uri,
            "scope": ",".join(self.SCOPES),
            "response_type": "code",
            "state": state,
        }
        return f"https://www.facebook.com/{settings.meta_graph_api_version}/dialog/oauth?{urlencode(params)}"

    async def handle_oauth_callback(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            token_resp = await client.get(
                f"{self._graph_url}/oauth/access_token",
                params={
                    "client_id": settings.meta_app_id,
                    "client_secret": settings.meta_app_secret,
                    "redirect_uri": settings.meta_redirect_uri,
                    "code": code,
                },
            )
            token_resp.raise_for_status()
            short_lived = token_resp.json()

            long_resp = await client.get(
                f"{self._graph_url}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": settings.meta_app_id,
                    "client_secret": settings.meta_app_secret,
                    "fb_exchange_token": short_lived["access_token"],
                },
            )
            long_resp.raise_for_status()
            return long_resp.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._graph_url}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": settings.meta_app_id,
                    "client_secret": settings.meta_app_secret,
                    "fb_exchange_token": refresh_token,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_account_info(self, access_token: str) -> SocialAccountInfo:
        async with httpx.AsyncClient() as client:
            pages_resp = await client.get(
                f"{self._graph_url}/me/accounts",
                params={"access_token": access_token},
            )
            pages_resp.raise_for_status()
            pages = pages_resp.json().get("data", [])
            if not pages:
                raise ValueError("No Facebook Pages linked to this account")

            page = pages[0]
            page_token = page["access_token"]
            page_id = page["id"]

            ig_resp = await client.get(
                f"{self._graph_url}/{page_id}",
                params={
                    "fields": "instagram_business_account{id,username,name,profile_picture_url,followers_count}",
                    "access_token": page_token,
                },
            )
            ig_resp.raise_for_status()
            ig_account = ig_resp.json().get("instagram_business_account", {})

            return SocialAccountInfo(
                account_id=ig_account.get("id", ""),
                username=ig_account.get("username", ""),
                display_name=ig_account.get("name", ""),
                profile_picture_url=ig_account.get("profile_picture_url"),
                followers_count=ig_account.get("followers_count"),
                metadata={"page_id": page_id, "page_token": page_token},
            )

    async def publish_image(
        self, access_token: str, account_id: str, image_url: str, caption: str, scheduled_at=None
    ) -> PublishResult:
        async with httpx.AsyncClient(timeout=60) as client:
            create = await client.post(
                f"{self._graph_url}/{account_id}/media",
                params={"image_url": image_url, "caption": caption, "access_token": access_token},
            )
            if create.status_code != 200:
                return PublishResult(success=False, error=create.text, raw_response=create.json() if create.content else {})
            creation_id = create.json().get("id")
            pub = await client.post(
                f"{self._graph_url}/{account_id}/media_publish",
                params={"creation_id": creation_id, "access_token": access_token},
            )
            if pub.status_code != 200:
                return PublishResult(success=False, error=pub.text, raw_response=pub.json() if pub.content else {})
            data = pub.json()
            return PublishResult(success=True, external_id=data.get("id"), raw_response=data)

    async def publish_carousel(
        self, access_token: str, account_id: str, media_urls: list[str], caption: str, scheduled_at=None
    ) -> PublishResult:
        async with httpx.AsyncClient(timeout=120) as client:
            child_ids = []
            for url in media_urls:
                r = await client.post(
                    f"{self._graph_url}/{account_id}/media",
                    params={"image_url": url, "is_carousel_item": "true", "access_token": access_token},
                )
                if r.status_code != 200:
                    return PublishResult(success=False, error=r.text)
                child_ids.append(r.json()["id"])
            create = await client.post(
                f"{self._graph_url}/{account_id}/media",
                params={
                    "media_type": "CAROUSEL",
                    "children": ",".join(child_ids),
                    "caption": caption,
                    "access_token": access_token,
                },
            )
            if create.status_code != 200:
                return PublishResult(success=False, error=create.text)
            creation_id = create.json()["id"]
            pub = await client.post(
                f"{self._graph_url}/{account_id}/media_publish",
                params={"creation_id": creation_id, "access_token": access_token},
            )
            if pub.status_code != 200:
                return PublishResult(success=False, error=pub.text)
            data = pub.json()
            return PublishResult(success=True, external_id=data.get("id"), raw_response=data)

    async def publish_reel(
        self, access_token: str, account_id: str, video_url: str, caption: str, cover_url=None, scheduled_at=None
    ) -> PublishResult:
        async with httpx.AsyncClient(timeout=180) as client:
            params = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": access_token,
            }
            if cover_url:
                params["cover_url"] = cover_url
            create = await client.post(f"{self._graph_url}/{account_id}/media", params=params)
            if create.status_code != 200:
                return PublishResult(success=False, error=create.text)
            creation_id = create.json()["id"]
            pub = await client.post(
                f"{self._graph_url}/{account_id}/media_publish",
                params={"creation_id": creation_id, "access_token": access_token},
            )
            if pub.status_code != 200:
                return PublishResult(success=False, error=pub.text)
            data = pub.json()
            return PublishResult(success=True, external_id=data.get("id"), raw_response=data)

    async def get_posts(self, access_token: str, account_id: str, limit: int = 25) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._graph_url}/{account_id}/media",
                params={
                    "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                    "limit": limit,
                    "access_token": access_token,
                },
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def get_metrics(self, access_token: str, post_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._graph_url}/{post_id}/insights",
                params={
                    "metric": "impressions,reach,engagement,saved,shares",
                    "access_token": access_token,
                },
            )
            if resp.status_code == 200:
                return resp.json()
            return {}

    async def get_comments(self, access_token: str, post_id: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._graph_url}/{post_id}/comments",
                params={"fields": "id,text,timestamp,username,from,replies", "access_token": access_token},
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def reply_comment(self, access_token: str, comment_id: str, message: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._graph_url}/{comment_id}/replies",
                params={"message": message, "access_token": access_token},
            )
            resp.raise_for_status()
            return resp.json()

    async def disconnect(self, access_token: str) -> bool:
        return True
