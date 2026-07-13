from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="username required"
    )
    email: EmailStr = Field(
        ..., description="valid email address"
    )
    password: str = Field(
        ..., min_length=8, description="Password(min 8 characters)"
    )
    


class UserLogin(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="username required"
    )
    password: str = Field(
        ..., min_length=8, description="Password required"
    )


class verifyEmail(BaseModel):
    email: EmailStr = Field(..., description="user email address")
    code: str = Field(..., description="verification code")

