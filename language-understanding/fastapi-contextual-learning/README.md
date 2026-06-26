# Contextual Learning with FastAPI

## Part 1: Framework Comparison — Translation Table

| Flask / Django Concept | FastAPI Equivalent | Key Difference |
|---|---|---|
| **Flask Blueprint** / **Django URL conf** | `APIRouter` | FastAPI routers are self-contained objects attached to the app; no central `urlpatterns` list |
| **Flask `@app.route`** | `@app.get`, `@app.post`, etc. | FastAPI uses explicit HTTP method decorators, not a single `methods=` param |
| **Flask request globals** (`request.args`, `request.json`) | Function parameters | FastAPI declares data as typed params; no global `request` object needed |
| **Django ModelForm / DRF Serializer** | Pydantic `BaseModel` | Validation happens at the boundary (request in, response out), not as a separate form/serializer layer |
| **Flask `request.get_json()` manual parsing** | Auto-parsed request body via Pydantic | FastAPI infers body from the param type; zero boilerplate parsing |
| **Django middleware** (process_request/process_response chain) | `Depends()` + `@app.middleware` | Middleware is for cross-cutting concerns; per-endpoint logic goes in dependencies |
| **Django auth middleware / Flask-Login** | `Depends(get_current_user)` | Authentication is a callable dependency, not middleware — easier to unit-test and opt-in per route |
| **Flask `g` / `current_app`** | `Depends()` for shared state | Dependencies are explicitly declared per endpoint; no implicit global state |
| **Django's QuerySet filtering** | List comprehensions + Pydantic | FastAPI doesn't dictate an ORM; you use native Python or an async ORM like SQLAlchemy 2.0 / Tortoise |
| **Flask-CORS extension** | `CORSMiddleware` from `fastapi.middleware.cors` | Built-in, no third-party extension needed |
| **Django's admin panel** | `/docs` (Swagger) + `/redoc` (ReDoc) | Auto-generated from type hints, not a manual admin config |
| **Django's `settings.py`** | Plain Python config / Pydantic `BaseSettings` | FastAPI has no built-in settings system — BYO config or use `pydantic-settings` |

### Philosophical Differences

| FastAPI | Flask | Django |
|---|---|---|
| Type-hint-driven | Convention-driven | Configuration-driven |
| Async-first | Sync-first (2.0+ async optional) | Sync-first (3.1+ async partial) |
| Declarative validation | Manual validation | Forms + DRF serializers |
| Dependency injection as a first-class citizen | No DI (manual wiring) | Middleware-based |

---

## Part 2: FastAPI's Design Philosophy

### Why Pydantic instead of built-in validation?
- **Reuse over reinvention** — Pydantic was already the best Python validation library. FastAPI layers on top rather than competing.
- **Type hints as source of truth** — Pydantic models double as schemas for validation *and* OpenAPI doc generation.
- **Separation of concerns** — FastAPI handles routing/DI; Pydantic handles data shape. Either can evolve independently.

### Why automatic API documentation?
- **Contract-first by default** — Every endpoint is documented without extra decorators or YAML files.
- **Interactive testing** — `/docs` eliminates the need for Postman/curl for exploration.
- **Client generation** — OpenAPI spec enables auto-generating TypeScript, Swift, Kotlin clients.

### Why extensive type hints?
- **Editor support** — autocomplete, refactoring, and static analysis work out of the box.
- **Validation for free** — `int`, `str`, `Optional[x]` become runtime validation rules with zero extra code.
- **Self-documenting** — the function signature *is* the API contract. No docstring required for basic understanding.

### Why async-first?
- **I/O-bound workloads dominate APIs** — DB queries, HTTP calls, file reads all benefit from `async`.
- **Starlette foundation** — built on ASGI, synchronous code runs in a thread pool automatically.
- **Future-proof** — as Python's async ecosystem matures (async ORMs, HTTP clients), FastAPI doesn't need a rewrite.

### How philosophy shapes application structure

```
Sync/imperative mindset (Flask):          Async/declarative mindset (FastAPI):

def create_item():                        async def create_item(item: ItemCreate, db=Depends(get_db)):
    data = request.get_json()                 # type hint declares shape and validation
    validate(data)                            # validation happens before the function runs
    item = db.insert(data)                    # db dependency is injected, not imported
    return jsonify(item)                      # return a dict/Pydantic model, FastAPI serializes it
```

---

## Part 3: JWT Authentication App

See [`jwt_auth/`](jwt_auth/) for the full implementation.

### Key patterns

1. **`OAuth2PasswordBearer`** — declares the token URL for Swagger UI's "Authorize" button
2. **`Depends(get_current_user)`** — authentication is a callable dependency, not middleware
3. **`Depends(get_current_active_user)`** — layers authorization on top of authentication
4. **Dependency chain** — `get_current_user` depends on `oauth2_scheme`; endpoints depend on `get_current_active_user`

### Run
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
uvicorn jwt_auth.main:app --reload
```

### Usage
1. POST `{"username": "johndoe", "password": "secret"}` to `/token`
2. Copy the `access_token` from the response
3. Click "Authorize" in Swagger UI and paste `Bearer {token}`
4. Hit `GET /users/me/` or `GET /users/me/items/`

---

## Part 4: Mental Model Translation

### Mental model: "The Dependency Injection Pyramid"

```
         ┌─────────────────────────────┐
         │    Endpoint functions        │  ← async def root(current_user = Depends(...))
         │  (pure request handlers)     │
         ├─────────────────────────────┤
         │    Dependencies              │  ← Depends(get_current_user), Depends(get_db)
         │  (auth, DB, config)          │
         ├─────────────────────────────┤
         │    Pydantic models           │  ← ItemCreate, TokenData, User
         │  (validation layer)          │
         ├─────────────────────────────┤
         │    Starlette                 │  ← Routing, middleware, WebSocket
         │  (ASGI foundation)           │
         ├─────────────────────────────┤
         │    Uvicorn                   │  ← ASGI server, event loop
         │  (runtime)                   │
         └─────────────────────────────┘
```

### Concept mapping (Flask → FastAPI mental model update)

| Your existing mental model | FastAPI mental model |
|---|---|
| "Import and call" — `from flask import request; data = request.get_json()` | "Declare and receive" — `async def handler(data: MyModel)` |
| "Middleware wraps everything" — `app.before_request` / `app.after_request` | "Inject exactly what you need" — `Depends()` per endpoint |
| "Manual serialization" — `jsonify(result)` | "Return a dict/model" — FastAPI serializes |
| "Validation at the function body" — `if not data.get('name'): abort(400)` | "Validation at the function boundary" — type hints + Pydantic |
| "Configuration in a file" — `app.config.from_pyfile('settings.py')` | "Config as dependencies" — `Settings = Depends(get_settings)` |
| "Test with request context" — `with app.test_request_context():` | "Test with `TestClient`" — `client = TestClient(app)` |
| "Error handling per route" — `try/except` in each handler | "Error handling via exception handlers" — `@app.exception_handler(MyError)` |

### Key mental shift

> **In Flask/Django, you *write code that handles requests*.**
> **In FastAPI, you *declare what your endpoint needs* and the framework wires it together.**

This is the same shift as going from imperative programming (how) to declarative programming (what). Type hints aren't just for static analysis — they're the primary mechanism for declaring structure, validation, and dependencies.
