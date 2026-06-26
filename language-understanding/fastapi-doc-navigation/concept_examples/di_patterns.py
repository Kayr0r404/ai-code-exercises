"""Dependency injection patterns — based on FastAPI docs on Dependencies."""

from fastapi import FastAPI, Depends, Header, HTTPException

app = FastAPI()


# Pattern 1: Simple dependency — a plain function
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "valid_key_123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# Pattern 2: Chained dependencies — one Depends calls another
async def get_current_user(api_key: str = Depends(verify_api_key)):
    return {"user_id": 123, "name": "Demo User", "api_key": api_key}


@app.get("/profile/")
async def read_profile(user: dict = Depends(get_current_user)):
    return {
        "message": f"Hello, {user['name']}!",
        "profile_data": {"subscription": "premium"},
    }


# Pattern 3: Dependency as a callable class
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def list_items(pagination: Pagination = Depends()):
    return {"skip": pagination.skip, "limit": pagination.limit, "items": []}
