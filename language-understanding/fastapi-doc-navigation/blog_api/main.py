from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.posts import router as posts_router

app = FastAPI(
    title="Blog API",
    description="A RESTful blog API with auth, posts, comments, and search — built from FastAPI documentation patterns",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(posts_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to the Blog API",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "posts": "GET/POST /posts/",
            "post_detail": "GET/PUT/DELETE /posts/{id}",
            "comments": "GET/POST /posts/{id}/comments/",
        },
    }
