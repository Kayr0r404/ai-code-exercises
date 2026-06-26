from fastapi import FastAPI
from .routes import items
from .utils.exceptions import add_exception_handlers

app = FastAPI(
    title="Enhanced FastAPI Example",
    description="A more structured FastAPI application with proper models and error handling",
    version="0.2.0",
)

app.include_router(items.router)
add_exception_handlers(app)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to the enhanced FastAPI example",
        "docs": "/docs",
        "endpoints": {
            "items": "/items"
        },
    }
