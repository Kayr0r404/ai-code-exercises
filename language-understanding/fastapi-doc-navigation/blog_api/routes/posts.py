from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime

from ..models.schemas import PostCreate, PostUpdate, PostResponse, CommentCreate, CommentResponse, UserPublic
from ..auth.deps import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

posts_db: dict[int, dict] = {}
next_post_id = 1
comments_db: dict[int, list[dict]] = {}
next_comment_id = 1


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(body: PostCreate, current_user: UserPublic = Depends(get_current_user)):
    global next_post_id
    pid = next_post_id
    next_post_id += 1
    post = {
        "id": pid,
        "title": body.title,
        "content": body.content,
        "published": body.published,
        "created_at": datetime.utcnow(),
        "author_id": current_user.id,
        "author": current_user,
    }
    posts_db[pid] = post
    comments_db[pid] = []
    return PostResponse(**post)


@router.get("/", response_model=list[PostResponse])
async def list_posts(
    q: Optional[str] = Query(None, min_length=1, description="Search by title or content"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    items = list(posts_db.values())
    if q:
        q_lower = q.lower()
        items = [
            p for p in items
            if q_lower in p["title"].lower() or q_lower in p["content"].lower()
        ]
    return [PostResponse(**p) for p in items[skip : skip + limit]]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse(**posts_db[post_id])


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    body: PostUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    post = posts_db[post_id]
    if post["author_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")

    if body.title is not None:
        post["title"] = body.title
    if body.content is not None:
        post["content"] = body.content
    if body.published is not None:
        post["published"] = body.published
    return PostResponse(**post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: UserPublic = Depends(get_current_user),
):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    if posts_db[post_id]["author_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    del posts_db[post_id]
    comments_db.pop(post_id, None)
    return None


# ── Comments ──────────────────────────────────────

@router.post("/{post_id}/comments/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    body: CommentCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    global next_comment_id
    cid = next_comment_id
    next_comment_id += 1
    comment = {
        "id": cid,
        "content": body.content,
        "created_at": datetime.utcnow(),
        "author": current_user,
    }
    comments_db[post_id].append(comment)
    return CommentResponse(**comment)


@router.get("/{post_id}/comments/", response_model=list[CommentResponse])
async def list_comments(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return [CommentResponse(**c) for c in comments_db.get(post_id, [])]
