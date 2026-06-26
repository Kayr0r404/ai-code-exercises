# Understanding FastAPI Code Patterns

## Part 1: Analyzing Complex Code

### Pattern 1: Generic Repository (`Repository[T]`)

```python
T = TypeVar("T", bound=Base)

class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[T]:
        ...
```

**Purpose:** Decouples data access logic from business logic. Instead of writing SQL/queries in route handlers, all DB logic lives in one place per model.

**Why `Generic[T]`?** Without it, you'd need a separate `UserRepository`, `PostRepository`, `CommentRepository` with identical `get_by_id` / `list` methods. The generic lets you reuse those and only write model-specific methods like `get_by_username`.

```python
class UserRepository(Repository[User]):   # inherits get_by_id, list
    async def get_by_username(...)         # only add the custom method
```

### Pattern 2: Service Layer

```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
```

**Purpose:** Encapsulates *business logic* (auth, token creation, password verification) between the route handler and the repository. Routes stay thin — they delegate to services.

**Flow:** Route → Service → Repository → DB

### Pattern 3: Dependency Injection Chain

```
get_db()              → yields AsyncSession (with cleanup)
oauth2_scheme         → extracts Bearer token from Authorization header
get_current_user()    → depends on oauth2_scheme + get_db
get_current_user      → injected into endpoints
```

Each dependency is:
- **Testable** in isolation — mock `get_db`, test `get_current_user` with a fake token
- **Composable** — dependencies can depend on other dependencies
- **Self-documenting** — the function signature declares exactly what it needs

### Pattern 4: Role-Based Access Control (RBAC)

```python
def requires_role(role: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            if role == "admin" and not current_user.is_superuser:
                raise HTTPException(status_code=403, ...)
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

**How it works:**
1. `@requires_role("admin")` wraps the endpoint
2. The wrapper declares `current_user: User = Depends(get_current_user)` as a parameter
3. FastAPI's DI resolves `get_current_user` before the wrapper body runs
4. If the user lacks `is_superuser`, the wrapper raises 403 before the endpoint runs

**Caveat:** This uses `Depends()` inside the decorator closure, which only works because FastAPI inspects the wrapper's signature at startup. It's clever but can confuse static analyzers. An alternative is a plain `Depends` that performs the check:

```python
async def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, ...)

@app.get("/admin/users/")
async def list_users(
    ..., admin: None = Depends(require_admin), current_user=Depends(get_current_user)
):
    ...
```

---

## Part 2: Tracing Execution Flow

### Request: `GET /admin/users/?skip=0&limit=10`

```
CLIENT
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  1. ASGI Server (Uvicorn) receives HTTP request              │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  2. TimingMiddleware.__call__()                              │
│     • Records start_time                                     │
│     • Calls call_next(request) → enters router               │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Router matches /admin/users/ → list_users()             │
│     • @requires_role("admin") decorator wrapper activated    │
│     • FastAPI inspects wrapper params for Depends()          │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  4. DI resolves get_current_user                             │
│     ┌─────────────────────────────────────────────────┐     │
│     │ 4a. oauth2_scheme extracts Bearer token from    │     │
│     │     Authorization header → "eyJhbGci..."        │     │
│     └─────────────────────────────────────────────────┘     │
│     │                                                       │
│     ▼                                                       │
│     ┌─────────────────────────────────────────────────┐     │
│     │ 4b. jwt.decode(token, "SECRET_KEY", ...)        │     │
│     │     Extracts payload: {"sub": "admin_user"}     │     │
│     └─────────────────────────────────────────────────┘     │
│     │                                                       │
│     ▼                                                       │
│     ┌─────────────────────────────────────────────────┐     │
│     │ 4c. get_db() yields AsyncSession                │     │
│     │     (also resolved via DI)                      │     │
│     └─────────────────────────────────────────────────┘     │
│     │                                                       │
│     ▼                                                       │
│     ┌─────────────────────────────────────────────────┐     │
│     │ 4d. UserRepository.get_by_username(db, "admin") │     │
│     │     SELECT * FROM users WHERE username = 'admin'│     │
│     │     Returns User(is_superuser=True)             │     │
│     └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  5. requires_role wrapper checks:                           │
│     role == "admin" AND current_user.is_superuser == True    │
│     → Pass. Proceeds to original list_users()               │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  6. list_users() body executes                               │
│     • UserRepository(User).list(db, skip=0, limit=10)       │
│     • SELECT * FROM users OFFSET 0 LIMIT 10                 │
│     • Returns list of User objects                           │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  7. FastAPI serializes response via response_model           │
│     • Converts User ORM objects → UserSchema (Pydantic)     │
│     • response_model=List[UserSchema] filters fields        │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│  8. TimingMiddleware recovers control                       │
│     • Calculates elapsed time                               │
│     • Sets X-Process-Time header                            │
│     • Returns Response to client                            │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
CLIENT receives JSON array of users + X-Process-Time header
```

### Dependency resolution order (key insight)

FastAPI resolves all `Depends()` **before** the decorator wrapper body runs. This means `get_current_user` runs *inside* the `requires_role` wrapper, so by the time the wrapper checks `current_user.is_superuser`, the token is already validated and the DB user is already fetched.

### Middleware vs. DI boundaries

| Layer | What it handles |
|---|---|
| **TimingMiddleware** | Cross-cutting: timing, logging, CORS — every request |
| **`@requires_role`** | Authorization check for a subset of endpoints |
| **`Depends(get_current_user)`** | Authentication — who is this? |
| **Endpoint body** | Business logic — what do they want to do? |

---

## Part 3: Simplifying Complex Concepts

### `@asynccontextmanager` + `lifespan`

**Problem:** Before FastAPI, startup/shutdown logic (connect DB, warm caches, close connections) was done with `@app.on_event("startup")` / `@app.on_event("shutdown")`. These worked but mixed concerns.

**Solution:** A single `lifespan` async context manager:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs when the server starts
    print("Connecting to database...")
    yield
    # Shutdown: runs when the server stops (gracefully)
    print("Closing connections...")
```

Think of it as: everything before `yield` is `__enter__`, everything after is `__exit__`.

### `TimingMiddleware`

**How it works:** Every HTTP request passes through this class. It:
1. Snaps a timestamp before the request
2. Passes the request to the next layer via `call_next(request)`
3. Snaps another timestamp after the response comes back
4. Injects the delta into the response header

```python
class TimingMiddleware:
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start = datetime.utcnow()
        response = await call_next(request)    # ← hand off to router
        elapsed = (datetime.utcnow() - start).total_seconds() * 1000
        response.headers["X-Process-Time"] = str(elapsed)   # ← tag response
        return response
```

### JWT Authentication Flow (simplified)

```
1. Client sends POST /token with username + password
2. Server verifies credentials against DB
3. Server creates a JWT containing {"sub": username, "exp": timestamp}
4. Server signs the JWT with a secret key → returns "eyJhbGci..."
5. Client stores the token, sends it in every subsequent request
   as "Authorization: Bearer eyJhbGci..."
6. Server decodes and verifies the token on each request
7. If valid → extract username → look up user → inject into endpoint
8. If invalid → return 401
```

**Key insight:** JWT is *stateless* — the server doesn't need a session store. All the information is in the token itself (signed, not encrypted — never put secrets in a JWT).

---

## Part 4: Building Understanding — Audit Logging Extension

See [`app/extensions/audit.py`](app/extensions/audit.py) for the implementation.

### Feature design
Using the same patterns from the original codebase:
- **Repository pattern** — `AuditLogRepository` extends `Repository[AuditLog]`
- **DI chain** — `get_audit_service` → `AuditService.log_action()`
- **No middleware** — audit logging is opt-in per endpoint via `Depends()`

### Key additions

| File | Purpose |
|---|---|
| `models/audit.py` | `AuditLog` ORM model |
| `extensions/audit.py` | `AuditLogRepository`, `AuditService`, `Depends` factory |

### Usage in endpoints

```python
@app.post("/token")
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
):
    # ... authenticate ...
    await audit.log_action(username, "LOGIN", success=True)
    return {"access_token": token}
```

### How it reinforces the architecture

- **Repository** stays the same shape — just swap `User` for `AuditLog`
- **Service** wraps repository with business meaning (`log_action` vs `audit_repo.insert`)
- **DI** injects `AuditService` only where needed — no middleware overhead on public endpoints
- The execution trace for `/admin/users/` now gets an additional step after the endpoint: `audit.log_action("admin_user", "LIST_USERS", ...)`
