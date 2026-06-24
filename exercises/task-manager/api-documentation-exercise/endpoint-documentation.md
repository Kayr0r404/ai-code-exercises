# Product API — Endpoint Documentation

## Base URL

```
https://api.example.com
```

---

## GET /api/products

List all products with filtering, sorting, and pagination.

### Authentication

No authentication required.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `category` | string | No | — | Filter by product category (e.g., `electronics`, `clothing`) |
| `minPrice` | number | No | — | Minimum price filter (inclusive) |
| `maxPrice` | number | No | — | Maximum price filter (inclusive) |
| `sort` | string | No | `createdAt` | Field to sort results by |
| `order` | enum (`asc`, `desc`) | No | `desc` | Sort direction |
| `page` | integer | No | `1` | Page number (1-indexed) |
| `limit` | integer | No | `20` | Items per page (max: 100) |
| `inStock` | boolean (`true`) | No | — | When `true`, only return products with available stock |

### Response

**Status: 200 OK**

```json
{
  "products": [
    {
      "_id": "61fa9bcf5c130b2e6d675432",
      "name": "Wireless Headphones",
      "description": "High-quality wireless headphones with noise cancellation",
      "price": 89.99,
      "category": "electronics",
      "stockQuantity": 45,
      "createdAt": "2023-02-01T15:32:47.000Z",
      "updatedAt": "2023-03-15T09:21:08.000Z"
    }
  ],
  "pagination": {
    "total": 42,
    "page": 1,
    "limit": 20,
    "pages": 3
  }
}
```

### Error Responses

**Status: 500 Internal Server Error**

```json
{
  "error": "Server error",
  "message": "Failed to fetch products"
}
```

### Examples

#### Example 1: Get electronics with price between $20 and $100

```
GET /api/products?category=electronics&minPrice=20&maxPrice=100&sort=price&order=asc&page=1&limit=10
```

Response:
```json
{
  "products": [
    {
      "_id": "61fa9bcf5c130b2e6d675432",
      "name": "Wireless Headphones",
      "description": "High-quality wireless headphones with noise cancellation",
      "price": 89.99,
      "category": "electronics",
      "stockQuantity": 45,
      "createdAt": "2023-02-01T15:32:47.000Z",
      "updatedAt": "2023-03-15T09:21:08.000Z"
    },
    {
      "_id": "61fa9bcf5c130b2e6d675435",
      "name": "Bluetooth Speaker",
      "description": "Portable bluetooth speaker with 20 hour battery life",
      "price": 49.99,
      "category": "electronics",
      "stockQuantity": 32,
      "createdAt": "2023-01-25T14:22:19.000Z",
      "updatedAt": "2023-03-10T11:05:24.000Z"
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "limit": 10,
    "pages": 2
  }
}
```

#### Example 2: Get in-stock products sorted by newest

```
GET /api/products?inStock=true&sort=createdAt&order=desc&page=1&limit=5
```

### Special Considerations

- All timestamps are returned in ISO 8601 format (UTC)
- Product IDs are MongoDB ObjectId strings
- Maximum `limit` per page is 100 items
- Empty results return `"products": []` with `pagination.total: 0`
- No rate limiting is currently implemented

---

## GET /api/products/:productId

Get a single product by its ID.

### Authentication

No authentication required.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productId` | string | Yes | MongoDB ObjectId of the product |

### Response

**Status: 200 OK**

```json
{
  "_id": "61fa9bcf5c130b2e6d675432",
  "name": "Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "price": 89.99,
  "category": "electronics",
  "stockQuantity": 45,
  "createdAt": "2023-02-01T15:32:47.000Z",
  "updatedAt": "2023-03-15T09:21:08.000Z"
}
```

### Error Responses

**Status: 400 Bad Request** — Invalid ID format

```json
{
  "error": "Invalid ID",
  "message": "Invalid product ID format"
}
```

**Status: 404 Not Found** — Product does not exist

```json
{
  "error": "Not found",
  "message": "Product not found"
}
```

**Status: 500 Internal Server Error** — Unexpected server error

```json
{
  "error": "Server error",
  "message": "Failed to fetch product"
}
```

### Examples

#### Example 1: Get a product by valid ID

```
GET /api/products/61fa9bcf5c130b2e6d675432
```

Response: 200 OK with full product object.

#### Example 2: Get a product with invalid ID format

```
GET /api/products/invalid-id-123
```

Response:
```json
{
  "error": "Invalid ID",
  "message": "Invalid product ID format"
}
```

### Special Considerations

- The `productId` must be a valid 24-character MongoDB ObjectId hex string
- A `CastError` in Mongoose indicates the ID format is invalid
