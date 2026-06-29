import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CommentStatus, PostStatus, PostType, SocialNetwork, UserRole


# --- Companies ---
class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    website: str | None = None
    brand_description: str | None = None
    tone: str | None = "professional"
    language: str = "es"
    target_audience: str | None = None
    location: str | None = None
    custom_hashtags: list[str] = []
    forbidden_words: list[str] = []


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    brand_description: str | None = None
    tone: str | None = None
    language: str | None = None
    colors: dict | None = None
    target_audience: str | None = None
    location: str | None = None
    custom_hashtags: list[str] | None = None
    forbidden_words: list[str] | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    website: str | None
    brand_description: str | None
    tone: str | None
    language: str
    colors: dict | None
    target_audience: str | None
    location: str | None
    custom_hashtags: list[str] | None
    forbidden_words: list[str] | None

    model_config = {"from_attributes": True}


# --- Social ---
class SocialAccountResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    network: SocialNetwork
    username: str | None
    display_name: str | None
    profile_picture_url: str | None
    is_connected: bool
    connected_at: datetime | None

    model_config = {"from_attributes": True}


# --- Posts ---
class PostCreate(BaseModel):
    company_id: uuid.UUID
    social_account_id: uuid.UUID | None = None
    type: PostType = PostType.IMAGE
    title: str | None = None
    caption: str | None = None
    hashtags: list[str] = []
    cta: str | None = None
    scheduled_at: datetime | None = None
    media_urls: list[str] = []
    ai_config: dict = {}


class PostUpdate(BaseModel):
    title: str | None = None
    caption: str | None = None
    hashtags: list[str] | None = None
    cta: str | None = None
    scheduled_at: datetime | None = None
    status: PostStatus | None = None
    media_urls: list[str] | None = None


class PostResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    social_account_id: uuid.UUID | None
    type: PostType
    status: PostStatus
    title: str | None
    caption: str | None
    hashtags: list[str] | None
    cta: str | None
    scheduled_at: datetime | None
    published_at: datetime | None
    external_post_id: str | None
    permalink: str | None
    error_message: str | None
    media_urls: list[str] = []

    model_config = {"from_attributes": True}


# --- AI ---
class GenerateContentRequest(BaseModel):
    company_id: uuid.UUID
    concept: str = Field(min_length=10, max_length=2000)
    text_provider: str | None = None
    text_model: str | None = None


class GenerateImageRequest(BaseModel):
    company_id: uuid.UUID
    prompt: str = Field(min_length=5, max_length=2000)
    provider: str = "openai"
    model: str | None = None
    width: int = 1024
    height: int = 1024


class AIContentResponse(BaseModel):
    title: str
    text: str
    description: str
    cta: str
    hashtags: list[str]
    seo: dict
    image_prompt: str
    video_prompt: str
    reel_ideas: list[str]
    story_ideas: list[str]
    carousel_ideas: list[str]
    variants: list[str]
    tones: list[str]
    provider: str
    model: str
    cost: float = 0
    duration_ms: float = 0


# --- Comments ---
class CommentReplyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2200)
    use_ai: bool = False


class CommentResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    external_comment_id: str | None
    author_username: str | None
    text: str
    status: CommentStatus
    reply_text: str | None
    ai_replied: bool

    model_config = {"from_attributes": True}


# --- Dashboard ---
class DashboardResponse(BaseModel):
    scheduled_posts: int
    published_posts: int
    failed_posts: int
    pending_comments: int
    total_engagement: int
    total_reach: int
    ai_calls: int
    ai_cost: float
    credits_balance: int
    followers: int
    upcoming_posts: list[PostResponse]
