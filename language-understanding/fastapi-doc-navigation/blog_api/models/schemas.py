from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── User ──────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserPublic(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Blog Post ─────────────────────────────────────

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = True


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    author: UserPublic

    class Config:
        from_attributes = True


# ── Comment ───────────────────────────────────────

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserPublic

    class Config:
        from_attributes = True
