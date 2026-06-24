# Developer Guide — Products API

> **Target audience:** Frontend and mobile developers integrating with the Products API. You should be comfortable with HTTP requests and JSON.
>
> **Tone:** Friendly and practical. We focus on what you need to get up and running.

---

## 1. Authentication

The Products API does not require authentication for read endpoints. Both `GET /api/products` and `GET /api/products/:productId` are publicly accessible.

> If you need write access (creating/updating products), your project will need to implement authentication separately. Check your project's auth documentation.

---

## 2. Making requests

### Base URL

```
https://api.example.com
```

All requests should include the `Content-Type: application/json` header.

### List products

```
GET https://api.example.com/api/products
```

The list endpoint accepts query parameters for filtering, sorting, and pagination. Parameters are appended to the URL:

```
GET https://api.example.com/api/products?category=electronics&minPrice=10&maxPrice=50&sort=price&order=asc&page=1&limit=20
```

### Get a single product

```
GET https://api.example.com/api/products/{productId}
```

Replace `{productId}` with the 24-character MongoDB ObjectId.

### Example code

#### cURL

```bash
# List electronics sorted by price ascending
curl "https://api.example.com/api/products?category=electronics&sort=price&order=asc&page=1&limit=10"

# Get a specific product
curl "https://api.example.com/api/products/61fa9bcf5c130b2e6d675432"
```

#### JavaScript (fetch)

```javascript
// List products with filters
async function listProducts(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`https://api.example.com/api/products?${params}`);
  return response.json();
}

// Usage
const result = await listProducts({
  category: 'electronics',
  minPrice: '20',
  maxPrice: '100',
  sort: 'price',
  order: 'asc',
  page: '1',
  limit: '10'
});

console.log(result.products);
console.log(`Page ${result.pagination.page} of ${result.pagination.pages}`);
```

#### Python (requests)

```python
import requests

def list_products(category=None, min_price=None, max_price=None,
                  sort='createdAt', order='desc', page=1, limit=20):
    params = {
        'category': category,
        'minPrice': min_price,
        'maxPrice': max_price,
        'sort': sort,
        'order': order,
        'page': page,
        'limit': limit
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get('https://api.example.com/api/products', params=params)
    response.raise_for_status()
    return response.json()

# Usage
result = list_products(category='electronics', min_price=20, max_price=100)
for product in result['products']:
    print(f"{product['name']} — ${product['price']}")
```

#### Node.js (axios)

```javascript
const axios = require('axios');

async function getProductById(productId) {
  try {
    const response = await axios.get(
      `https://api.example.com/api/products/${productId}`
    );
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(`Error ${error.response.status}:`, error.response.data);
    }
    throw error;
  }
}

// Usage
getProductById('61fa9bcf5c130b2e6d675432')
  .then(product => console.log(product.name))
  .catch(err => console.error('Failed to fetch product'));
```

---

## 3. Handling responses

### Success responses

**List endpoint** returns an object with two fields:

| Field | Type | Description |
|-------|------|-------------|
| `products` | array | Array of product objects (may be empty) |
| `pagination` | object | Pagination metadata |

Each product object has these fields:

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | MongoDB ObjectId (24 hex characters) |
| `name` | string | Product name |
| `description` | string | Product description |
| `price` | number | Price in USD |
| `category` | string | Category slug |
| `stockQuantity` | integer | Available stock |
| `createdAt` | string | ISO 8601 UTC timestamp |
| `updatedAt` | string | ISO 8601 UTC timestamp |

**Single product endpoint** returns the product object directly.

### Pagination

The `pagination` object tells you how many results exist and how to navigate:

```json
{
  "pagination": {
    "total": 42,
    "page": 1,
    "limit": 20,
    "pages": 3
  }
}
```

| Field | Description |
|-------|-------------|
| `total` | Total matching products across all pages |
| `page` | Current page number |
| `limit` | Items per page |
| `pages` | Total pages available |

To get the next page, increment `page`:
```
GET /api/products?page=2
```

If `page > pages`, you'll get an empty `products` array with the same pagination metadata.

---

## 4. Error handling

### Error response format

All errors return the same structure:

```json
{
  "error": "Error type",
  "message": "Human-readable description"
}
```

### Common errors

| Status | Error Type | Likely Cause | What to Do |
|--------|-----------|-------------|------------|
| 400 | `Invalid ID` | `productId` is not a valid 24-char hex string | Check the ID format. See note below. |
| 404 | `Not found` | Product doesn't exist | Verify the `productId` is correct. |
| 500 | `Server error` | Database or server issue | Retry with exponential backoff. Contact support if it persists. |

> **Tip:** A 400 error for an invalid ID means the data type is wrong — if your Product ID from MongoDB is `ObjectId('...')`, make sure you're serializing it to its hex string form before passing it to the API.

### Defensive coding pattern

Always check `response.ok` or wrap in try/catch:

```javascript
async function safeGetProduct(id) {
  const response = await fetch(`https://api.example.com/api/products/${id}`);

  if (!response.ok) {
    const error = await response.json();
    console.warn(`Request failed (${response.status}): ${error.message}`);
    return null;
  }

  return response.json();
}
```

---

## 5. Best practices

- **Use pagination** — always pass `page` and `limit` explicitly for predictable results
- **Don't exceed limit 100** — the API caps at 100 items per page
- **Parse timestamps** — `createdAt` and `updatedAt` are ISO 8601 UTC strings; parse them with `new Date()` in JS or `datetime.fromisoformat()` in Python
- **Cache responses** — product data doesn't change frequently; consider caching with a reasonable TTL
- **Handle empty results** — `products` will be an empty array when no products match; check `pagination.total === 0`
