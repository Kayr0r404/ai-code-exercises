"""Pydantic models for request/response — based on FastAPI docs on Body and Response Model."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# Request model with validation
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


# Response model — no password exposed
class UserResponse(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    id: int


# Nested model
class Tag(BaseModel):
    name: str = Field(..., max_length=30)


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    tags: list[Tag] = []
