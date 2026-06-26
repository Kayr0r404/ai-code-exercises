from fastapi import FastAPI
from .routes.todos import router as todos_router

app = FastAPI(
    title="To-Do List API",
    description="A simple to-do list manager built with FastAPI",
    version="1.0.0",
)

app.include_router(todos_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to the To-Do List API",
        "docs": "/docs",
        "endpoints": {
            "create_todo": "POST /todos/",
            "list_todos": "GET /todos/?status=completed|pending",
            "complete_todo": "PATCH /todos/{id}/complete",
            "delete_todo": "DELETE /todos/{id}",
        },
    }
