"""Path, Query, Header, Cookie parameters — based on FastAPI docs."""

from fastapi import FastAPI, Path, Query, Header, Cookie
from typing import Optional

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="Item ID", gt=0),
    q: Optional[str] = Query(None, min_length=3, max_length=50),
    limit: int = Query(10, ge=1, le=100),
    user_agent: Optional[str] = Header(None),
    session: Optional[str] = Cookie(None),
):
    return {
        "item_id": item_id,
        "q": q,
        "limit": limit,
        "user_agent": user_agent,
        "session": session,
    }
