"""Dependency with yield for cleanup — FastAPI docs on Dependencies with yield."""

from fastapi import FastAPI

app = FastAPI()


async def get_db():
    db = {"connection": "open"}
    try:
        yield db
    finally:
        db["connection"] = "closed"


@app.get("/users/")
async def list_users(db: dict = Depends(get_db)):
    assert db["connection"] == "open"
    return [{"id": 1, "name": "Alice"}]
