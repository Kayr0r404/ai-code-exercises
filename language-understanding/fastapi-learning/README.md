# FastAPI Learning Exercise

## Part 1: FastAPI Fundamentals

### What is FastAPI?

**FastAPI** is a modern, fast (high-performance) Python web framework for building APIs with Python 3.7+. It's built on top of Starlette (for web routing) and Pydantic (for data validation).

| Aspect | FastAPI | Flask | Django |
|---|---|---|---|
| **Type validation** | Built-in via Pydantic | Manual or addons | DRF serializers |
| **Async support** | Native (async/await) | Limited (Flask 2.0+) | Via Django Channels or 3.1+ |
| **Auto docs** | OpenAPI + Swagger/ReDoc auto-generated | Manual | DRF + drf-yasg |
| **Performance** | Near Node.js/Go level (Starlette) | Good | Lower (synced, heavier) |
| **Learning curve** | Moderate (needs type hints) | Shallow | Steep |
| **Use case** | APIs, microservices, real-time | Small apps, prototypes | Full-stack monoliths |

### Core Concepts

- **Path operations**: Function + decorator (`@app.get("/")`) defining an endpoint
- **Path parameters**: Variables captured from URL path (`/items/{item_id}`)
- **Query parameters**: Optional params after `?` in URL (`?q=hello&limit=5`)
- **Request body**: JSON payload validated by Pydantic models
- **Dependency Injection**: Declare dependencies as function params; FastAPI resolves them
- **Type hints drive everything**: validation, serialization, docs generation

### Key Advantages

1. **Automatic interactive docs** — `/docs` (Swagger) and `/redoc` (ReDoc) for free
2. **Editor support** — type hints enable autocomplete everywhere
3. **Async by design** — `async def` endpoints, no thread pool hacks
4. **Data validation** — Pydantic handles request/response validation automatically
5. **OpenAPI compliance** — generates full OpenAPI spec, easy to integrate with tools

### Essential Glossary

| Term | Definition |
|---|---|
| **Starlette** | ASGI framework underlying FastAPI; handles routing, middleware, WebSocket |
| **Pydantic** | Data validation library using Python type hints; `BaseModel` defines schemas |
| **Path operation** | A route + HTTP method combination (`@app.get`, `@app.post`, etc.) |
| **Path operation decorator** | The decorator that maps HTTP method/path to a function |
| **Path parameter** | Dynamic part of URL path, e.g. `{item_id}` in `/items/{item_id}` |
| **Query parameter** | Key=value pairs after `?` in URL; function params not in path |
| **Request body** | JSON payload sent by client, validated against a Pydantic model |
| **Dependency** | A callable declared as a function parameter; FastAPI injects its result |
| **ASGI** | Asynchronous Server Gateway Interface (successor to WSGI) |
| **Uvicorn** | ASGI server that runs FastAPI apps |
| **OpenAPI** | Standard specification for RESTful API documentation |
| **Swagger UI** | Interactive API documentation UI at `/docs` |

### Design Philosophy

- **"Don't fight the framework"** — follow type hint conventions and everything works
- **Declaration over imperative** — declare what you want (types, validation), the framework does it
- **Performance matters** — built on Starlette + Pydantic, benchmarks near Go/Node.js
- **Developer experience first** — auto-complete, auto-docs, auto-validation reduce iteration time

---

## Part 2: Hello World API

See [`main.py`](main.py) for the basic implementation. Run with:

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Then visit:
- http://127.0.0.1:8000/ — root greeting
- http://127.0.0.1:8000/items/42 — path param example
- http://127.0.0.1:8000/search?q=test — query param example
- http://127.0.0.1:8000/docs — Swagger UI

---

## Part 3: Enhanced Structure

See the [`app/`](app/) directory for the modular structure:
- `app/main.py` — app creation and config
- `app/models/item.py` — Pydantic models
- `app/routes/items.py` — route handlers
- `app/utils/exceptions.py` — custom error handling

Run with:
```bash
uvicorn app.main:app --reload
```

---

## Part 4: To-Do List API Challenge

See [`todo_app/`](todo_app/) for the full implementation.

### Features
- Create a to-do item (title, description, due date)
- List items with optional status filtering (completed/pending)
- Mark an item as completed
- Delete an item

### Run
```bash
uvicorn todo_app.main:app --reload
```
