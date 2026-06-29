import uuid

from pydantic import BaseModel, Field

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    organization_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class OrganizationSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    role: UserRole

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    organizations: list[OrganizationSummary] = []

    model_config = {"from_attributes": True}
