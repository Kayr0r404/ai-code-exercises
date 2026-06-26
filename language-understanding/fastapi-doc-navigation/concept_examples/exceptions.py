"""Exception handling patterns — based on FastAPI docs."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body,
        },
    )


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    if product_id == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found",
            headers={"X-Error-Code": "PRODUCT_NOT_FOUND"},
        )
    if product_id < 1:
        raise HTTPException(
            status_code=400, detail="Product ID must be positive"
        )
    return {"id": product_id, "name": "Sample Product", "price": 29.99}
