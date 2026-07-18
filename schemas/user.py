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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Account email address")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Account email address")
    token: str = Field(..., min_length=8, description="Reset token from email")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )

