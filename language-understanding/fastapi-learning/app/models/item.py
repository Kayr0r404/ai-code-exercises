from pydantic import BaseModel, Field
from typing import Optional, List


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the item")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    tags: List[str] = Field(default=[], description="List of tags for the item")


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "Powerful development machine",
                "price": 1299.99,
                "tags": ["electronics", "computers"]
            }
        }
