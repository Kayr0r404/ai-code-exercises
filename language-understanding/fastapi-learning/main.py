from fastapi import FastAPI

app = FastAPI(
    title="My First FastAPI App",
    description="A simple API built with FastAPI",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "message": f"You requested item {item_id}"}


@app.get("/search/")
async def search_items(q: str = None, skip: int = 0, limit: int = 10):
    return {
        "query": q,
        "skip": skip,
        "limit": limit,
        "message": f"Searching for '{q}' (skipping {skip}, limiting to {limit})"
    }
