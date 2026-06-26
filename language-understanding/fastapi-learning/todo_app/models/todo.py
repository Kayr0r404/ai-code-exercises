from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the to-do item")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")
    due_date: Optional[datetime] = Field(None, description="Optional due date")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
