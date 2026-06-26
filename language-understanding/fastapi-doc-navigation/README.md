# Documentation Navigation for FastAPI

## Part 1: Documentation Reading Roadmap

### Recommended reading order (from official docs)

| Order | Section | Why this order |
|---|---|---|
| 1 | [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) | Minimal working example in 10 lines |
| 2 | [Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) | Core routing concept |
| 3 | [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) | Second most common param type |
| 4 | [Request Body](https://fastapi.tiangolo.com/tutorial/body/) | Introduces Pydantic — the biggest shift |
| 5 | [Query Parameters & String Validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) | Shows `Query()` for the first time |
| 6 | [Path Parameters & Numeric Validations](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/) | `Path()` analog |
| 7 | [Body — Multiple Parameters](https://fastapi.tiangolo.com/tutorial/body-multiple-params/) | Mixing path, query, body, and `Field()` |
| 8 | [Body — Nested Models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) | Realistic data structures |
| 9 | [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) | The other half of Pydantic — output filtering |
| 10 | [Extra Models](https://fastapi.tiangolo.com/tutorial/extra-models/) | `Create` vs `Response` vs `Update` patterns |
| 11 | [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/) | The killer feature — changes everything |
| 12 | [Security](https://fastapi.tiangolo.com/tutorial/security/) | OAuth2 + JWT with `Depends()` |
| 13 | [Middleware](https://fastapi.tiangolo.com/tutorial/middleware/) | Cross-cutting concerns |
| 14 | [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) | Fire-and-forget patterns |
| 15 | [Testing](https://fastapi.tiangolo.com/tutorial/testing/) | `TestClient` with `httpx` |
| 16 | [Bigger Applications — Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/) | `APIRouter`, project structure |

### Top 5 sections for a quick REST API

1. **Path Parameters + Query Parameters + Request Body** — the three param types cover 90% of API needs
2. **Response Model** — controls what data is exposed; prevents password leaks, shapes JSON output
3. **Dependency Injection** — auth, DB sessions, config — all reusable wiring
4. **Security (OAuth2 + JWT)** — the de facto auth pattern for REST APIs
5. **Testing** — `TestClient` makes integration tests trivial

### DI documentation — key takeaways

| Documentation point | Practical application |
|---|---|
| Dependencies are just callables | Any function can be a dependency — no special decorators |
| `Depends()` accepts nested `Depends()` | Compose auth: `verify_api_key` → `get_current_user` → endpoint |
| Dependencies can be `async` or sync | FastAPI handles the thread pool transparently |
| Dependencies can return values or `None` | `Optional[User] = Depends(get_user_or_none)` for optional auth |
| `yield` for cleanup | DB session management: open on enter, close on exit |

---

## Part 2: Documentation Deep Dive — Dependency Injection

### Core concepts (`Depends`)

- **`Depends()` is a marker** — tells FastAPI "call this function and inject the result"
- **No `@inject` decorator** — FastAPI hijacks the regular function signature inspection
- **Composable** — `Depends(a)` can call `Depends(b)`; just nest them in the callable's own parameters
- **Not just for auth** — DI works for DB sessions, config, request preprocessing, permissions

### When to use `Depends` vs. alternatives

| Situation | Use | Reason |
|---|---|---|
| Share logic across endpoints | `Depends()` | DRY, testable in isolation |
| Cross-cutting concern (CORS, logging) | Middleware | Applies to all routes unconditionally |
| One-off logic in a single endpoint | Inline code | No abstraction overhead |
| Complex multi-step setup | Nested `Depends()` | Each step testable separately |
| State per-request (DB session) | `Depends()` with `yield` | Cleanup guaranteed |

### Common anti-patterns

```python
# BAD — importing a module-level client (hard to test, no cleanup)
from myapp.db import db_client

# GOOD — dependency injection (testable, cleanup via yield)
async def get_db():
    async with async_session() as session:
        yield session
```

---

## Part 3: Concept-to-Code Reference Guide

All code examples live in [`concept_examples/`](concept_examples/).

### 1. Dependency Injection patterns

| Pattern | Code file |
|---|---|
| Simple dependency (API key check) | `concept_examples/di_patterns.py` |
| Chained dependencies (API key → user) | `concept_examples/di_patterns.py` |
| `yield` for cleanup (DB session) | `concept_examples/di_yield.py` |
| Dependency classes (callable objects) | `concept_examples/di_patterns.py` |

### 2. Pydantic models for request/response

| Pattern | Code file |
|---|---|
| Request model with `Field()` validation | `concept_examples/pydantic_models.py` |
| Response model (filter password) | `concept_examples/pydantic_models.py` |
| Nested models | `concept_examples/pydantic_models.py` |

### 3. Background tasks

| Pattern | Code file |
|---|---|
| Fire-and-forget email | `concept_examples/background_tasks.py` |
| With dependency injection | `concept_examples/background_tasks.py` |

### 4. Parameter types

| Pattern | Code file |
|---|---|
| Path + Query + Header + Cookie in one endpoint | `concept_examples/params.py` |

### 5. Exception handling

| Pattern | Code file |
|---|---|
| Custom `HTTPException` | `concept_examples/exceptions.py` |
| Custom validation error handler | `concept_examples/exceptions.py` |

---

## Part 4: Blog API Mini-Application

See [`blog_api/`](blog_api/) for the full implementation.

### Features
- User registration (POST `/auth/register`)
- Login with JWT token (POST `/auth/login`)
- Create/read/update/delete blog posts (CRUD `/posts/`)
- Add comments to posts (`/posts/{id}/comments/`)
- Search posts by title/content (`GET /posts/?q=...`)

### Documentation references used

| Feature | FastAPI docs section |
|---|---|
| User model with validation | [Body — Nested Models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) |
| Password hashing + JWT | [OAuth2 with Password (and hashing)](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) |
| Dependency injection for auth | [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) |
| `APIRouter` for modular routes | [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) |
| Response model for output filtering | [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) |
| Search via query parameter | [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) |

### Run
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
uvicorn blog_api.main:app --reload
```

### API overview
```
POST /auth/register      — Register a new user
POST /auth/login         — Login, receive JWT
GET    /posts/           — List posts (optional ?q=search)
POST   /posts/           — Create a post (auth required)
GET    /posts/{id}       — Get a single post
PUT    /posts/{id}       — Update a post (author only)
DELETE /posts/{id}       — Delete a post (author only)
POST   /posts/{id}/comments/  — Add a comment (auth required)
```
