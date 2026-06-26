from fastapi import APIRouter, Path, Query, status
from typing import List, Optional
from datetime import datetime

from ..models.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

todos_db = {}
todo_counter = 0


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    global todo_counter
    todo_counter += 1
    new_todo = {
        "id": todo_counter,
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date,
        "completed": False,
        "created_at": datetime.now(),
    }
    todos_db[todo_counter] = new_todo
    return new_todo


@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter: 'completed' or 'pending'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    items = list(todos_db.values())
    if status_filter == "completed":
        items = [t for t in items if t["completed"]]
    elif status_filter == "pending":
        items = [t for t in items if not t["completed"]]
    return items[skip : skip + limit]


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(
    todo_id: int = Path(..., gt=0, description="ID of the to-do item to mark complete"),
):
    if todo_id not in todos_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    todos_db[todo_id]["completed"] = True
    return todos_db[todo_id]


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int = Path(..., gt=0, description="ID of the to-do item to delete"),
):
    if todo_id not in todos_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Todo with ID {todo_id} not found")
    del todos_db[todo_id]
    return None
