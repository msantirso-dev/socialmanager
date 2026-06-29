import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    OPERATOR = "operator"
    READONLY = "readonly"


class OrganizationPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SocialNetwork(str, enum.Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    THREADS = "threads"
    PINTEREST = "pinterest"
    GOOGLE_BUSINESS = "google_business"
    WORDPRESS = "wordpress"


class PostType(str, enum.Enum):
    IMAGE = "image"
    CAROUSEL = "carousel"
    REEL = "reel"
    VIDEO = "video"
    STORY = "story"
    TEXT = "text"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class CommentStatus(str, enum.Enum):
    PENDING = "pending"
    REPLIED = "replied"
    HIDDEN = "hidden"
    FLAGGED = "flagged"
    DELETED = "deleted"


class SchedulerJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class LogCategory(str, enum.Enum):
    API = "api"
    AI = "ai"
    SOCIAL = "social"
    SCHEDULER = "scheduler"
    AUTH = "auth"
    ERROR = "error"
    AUDIT = "audit"
