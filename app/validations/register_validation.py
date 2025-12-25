import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserRegistrationRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, upper, lower, digit, special)",
    )
    password_confirm: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Confirm password",
    )

    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")

    # ---------- password strength ----------
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^\w\s]", password):
            raise ValueError("Password must contain at least one special character")
        return password

    # ---------- password match ----------
    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
            }
        }
