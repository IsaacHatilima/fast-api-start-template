from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    id: UUID = Field(
        validation_alias="public_id",
        serialization_alias="id",
    )
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID = Field(
        validation_alias="public_id",
        serialization_alias="id",
    )
    email: EmailStr
    email_verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    profile: Optional[ProfileResponse]

    class Config:
        from_attributes = True
