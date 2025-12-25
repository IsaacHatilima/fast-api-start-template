from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    profile: Optional[ProfileResponse]

    class Config:
        from_attributes = True
