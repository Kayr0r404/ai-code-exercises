from fastapi import APIRouter, Path, Query, status
from typing import List, Optional

from ..models.item import ItemCreate, ItemResponse
from ..utils.exceptions import ItemNotFoundError

router = APIRouter(prefix="/items", tags=["items"])

fake_items_db = {}
item_counter = 0


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global item_counter
    item_counter += 1
    item_dict = item.model_dump()
    new_item = {**item_dict, "id": item_counter}
    fake_items_db[item_counter] = new_item
    return new_item


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to retrieve")
):
    if item_id not in fake_items_db:
        raise ItemNotFoundError(item_id)
    return fake_items_db[item_id]


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    tag: Optional[str] = Query(None, description="Filter items by tag"),
):
    items = list(fake_items_db.values())
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]
    return items[skip : skip + limit]
